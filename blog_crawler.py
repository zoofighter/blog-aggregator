"""
블로그 크롤러
RSS 피드에서 포스트를 수집하고 DB에 저장합니다.
"""

import re
import time
import sqlite3
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import feedparser
import requests
from bs4 import BeautifulSoup


class BlogCrawler:
    """RSS 피드 기반 블로그 크롤러"""

    def __init__(self, db_path: str = "blogs.db"):
        self.db_path = db_path
        self.user_agent = 'BlogAggregator/1.0 (Personal Blog Curator)'

    def crawl_all_blogs(self, limit_per_blog: int = 10, verbose: bool = False):
        """모든 활성 블로그 크롤링"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, feed_url
            FROM blogs
            WHERE active = TRUE AND feed_url IS NOT NULL AND feed_url != ''
        """)

        blogs = cursor.fetchall()
        conn.close()

        if not blogs:
            print("❌ 크롤링할 블로그가 없습니다.")
            return

        print(f"\n🚀 {len(blogs)}개 블로그 크롤링 시작...\n")

        total_new_posts = 0

        for i, (blog_id, blog_name, feed_url) in enumerate(blogs, 1):
            print(f"[{i}/{len(blogs)}] {blog_name}")

            try:
                new_posts = self.crawl_blog(blog_id, feed_url, limit=limit_per_blog, verbose=verbose)
                total_new_posts += new_posts

                if verbose:
                    print(f"   ✅ {new_posts}개 신규 포스트 수집\n")
                else:
                    print(f"   ✅ {new_posts}개 수집")

                # Rate limiting: 2초 대기
                if i < len(blogs):
                    time.sleep(2)

            except Exception as e:
                print(f"   ❌ 오류: {str(e)}\n")
                continue

        print(f"\n✅ 완료! 총 {total_new_posts}개 신규 포스트 수집")

        # 블로그의 last_crawled 업데이트
        self._update_last_crawled()

    def crawl_blog(self, blog_id: int, feed_url: str, limit: int = 10, verbose: bool = False) -> int:
        """개별 블로그 크롤링"""
        entries = self.parse_feed(feed_url)

        if not entries:
            if verbose:
                print("   ⚠️  피드에 항목이 없습니다.")
            return 0

        new_posts_count = 0

        for entry in entries[:limit]:  # 최대 limit개만 처리
            post_data = self.extract_post_data(entry, blog_id)

            if not post_data:
                continue

            # 중복 체크
            if self.is_duplicate(post_data['url']):
                if verbose:
                    print(f"   ⏭️  건너뜀 (중복): {post_data['title'][:50]}")
                continue

            # 요약 생성
            if post_data['content']:
                post_data['summary'] = self.generate_simple_summary(post_data['content'])

            # 저장
            if self.save_post(post_data):
                new_posts_count += 1
                if verbose:
                    print(f"   ✅ 저장: {post_data['title'][:50]}")

        return new_posts_count

    def parse_feed(self, feed_url: str) -> List:
        """RSS 피드 파싱"""
        try:
            # feedparser 사용
            feed = feedparser.parse(feed_url, agent=self.user_agent)

            if feed.bozo and feed.bozo_exception:
                # 에러가 있지만 일부 데이터는 파싱되었을 수 있음
                if not feed.entries:
                    raise Exception(f"피드 파싱 실패: {feed.bozo_exception}")

            return feed.entries

        except Exception as e:
            raise Exception(f"피드 로드 실패: {str(e)}")

    def extract_post_data(self, entry, blog_id: int) -> Optional[Dict]:
        """피드 항목에서 포스트 데이터 추출"""
        try:
            # 제목
            title = entry.get('title', '제목 없음').strip()

            # URL
            url = entry.get('link', '')
            if not url:
                return None

            # 작성자
            author = entry.get('author', '')

            # 발행일
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6])

            # 본문 추출
            content = ''

            # 1. content:encoded (브런치, 일부 블로그)
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value

            # 2. summary/description (네이버 블로그 등)
            elif hasattr(entry, 'summary'):
                content = entry.summary

            # 3. description
            elif hasattr(entry, 'description'):
                content = entry.description

            # 이미지 URL 추출
            image_url = self._extract_image_url(entry, content)

            return {
                'blog_id': blog_id,
                'title': title,
                'url': url,
                'author': author,
                'published_date': published_date,
                'content': content,
                'summary': '',  # 나중에 생성
                'image_url': image_url
            }

        except Exception as e:
            print(f"   ⚠️  포스트 데이터 추출 실패: {str(e)}")
            return None

    def _extract_image_url(self, entry, content: str) -> Optional[str]:
        """이미지 URL 추출"""
        # 1. media:thumbnail (RSS 표준)
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0]['url']

        # 2. media:content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'image' in media.get('type', ''):
                    return media.get('url')

        # 3. enclosure
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    return enclosure.get('href')

        # 4. HTML 본문에서 첫 번째 img 태그
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img['src']

        return None

    def generate_simple_summary(self, content: str, max_length: int = 200) -> str:
        """간단한 요약 생성 (HTML 제거 후 첫 200자)"""
        if not content:
            return ''

        # HTML 태그 제거
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # 공백 정리
        text = re.sub(r'\s+', ' ', text)

        # 200자로 자르기
        if len(text) > max_length:
            return text[:max_length] + '...'
        else:
            return text

    def is_duplicate(self, url: str) -> bool:
        """URL 기반 중복 체크"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE url = ?", (url,))
        count = cursor.fetchone()[0]

        conn.close()
        return count > 0

    def save_post(self, post_data: Dict) -> bool:
        """포스트 DB 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO posts (blog_id, title, url, author, published_date, content, summary, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data['blog_id'],
                post_data['title'],
                post_data['url'],
                post_data['author'],
                post_data['published_date'],
                post_data['content'],
                post_data['summary'],
                post_data['image_url']
            ))

            conn.commit()
            conn.close()
            return True

        except sqlite3.IntegrityError:
            # URL이 이미 존재 (UNIQUE 제약)
            return False
        except Exception as e:
            print(f"   ❌ DB 저장 실패: {str(e)}")
            return False

    def _update_last_crawled(self):
        """모든 블로그의 last_crawled 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE blogs
            SET last_crawled = CURRENT_TIMESTAMP
            WHERE active = TRUE AND feed_url IS NOT NULL
        """)

        conn.commit()
        conn.close()


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='블로그 크롤러')
    parser.add_argument('--blog-id', type=int, help='특정 블로그만 크롤링')
    parser.add_argument('--limit', type=int, default=10, help='블로그당 포스트 개수 제한 (기본: 10)')
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 출력')

    args = parser.parse_args()

    crawler = BlogCrawler()

    if args.blog_id:
        # 특정 블로그만 크롤링
        conn = sqlite3.connect(crawler.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, feed_url FROM blogs WHERE id = ?", (args.blog_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            print(f"❌ ID {args.blog_id} 블로그를 찾을 수 없습니다.")
            return

        blog_name, feed_url = result
        print(f"\n🔍 크롤링: {blog_name}\n")

        new_posts = crawler.crawl_blog(args.blog_id, feed_url, limit=args.limit, verbose=args.verbose)
        print(f"\n✅ 완료! {new_posts}개 신규 포스트 수집")

    else:
        # 모든 블로그 크롤링
        crawler.crawl_all_blogs(limit_per_blog=args.limit, verbose=args.verbose)


if __name__ == '__main__':
    main()
