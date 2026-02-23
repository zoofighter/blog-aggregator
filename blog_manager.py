"""
블로그 리스트 관리 도구
CSV 파일에서 블로그 정보를 읽고 관리합니다.
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import requests


class BlogManager:
    """블로그 소스 관리 클래스"""

    def __init__(self, db_path: str = "blogs.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 블로그 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                feed_url TEXT,
                category TEXT,
                priority TEXT DEFAULT 'medium',
                active BOOLEAN DEFAULT TRUE,
                description TEXT,
                tags TEXT,
                crawl_interval INTEGER DEFAULT 180,
                last_crawled TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 포스트 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                author TEXT,
                published_date TIMESTAMP,
                content TEXT,
                summary TEXT,
                image_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (blog_id) REFERENCES blogs(id)
            )
        """)

        conn.commit()
        conn.close()
        print(f"✅ 데이터베이스 초기화 완료: {self.db_path}")

    def load_from_csv(self, csv_path: str) -> int:
        """CSV 파일에서 블로그 로드"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        added_count = 0
        updated_count = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # 기존 블로그 확인
                cursor.execute("SELECT id FROM blogs WHERE url = ?", (row['url'],))
                existing = cursor.fetchone()

                if existing:
                    # 업데이트
                    cursor.execute("""
                        UPDATE blogs SET
                            name = ?,
                            feed_url = ?,
                            category = ?,
                            priority = ?,
                            active = ?,
                            description = ?,
                            tags = ?
                        WHERE url = ?
                    """, (
                        row['blog_name'],
                        row['feed_url'] or None,
                        row['category'],
                        row['priority'],
                        row['active'].lower() == 'true',
                        row['description'],
                        row['tags'],
                        row['url']
                    ))
                    updated_count += 1
                else:
                    # 새로 추가
                    cursor.execute("""
                        INSERT INTO blogs (name, url, feed_url, category, priority, active, description, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['blog_name'],
                        row['url'],
                        row['feed_url'] or None,
                        row['category'],
                        row['priority'],
                        row['active'].lower() == 'true',
                        row['description'],
                        row['tags']
                    ))
                    added_count += 1

        conn.commit()
        conn.close()

        print(f"✅ CSV 로드 완료: {added_count}개 추가, {updated_count}개 업데이트")
        return added_count + updated_count

    def export_to_csv(self, output_path: str):
        """데이터베이스에서 CSV로 내보내기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, url, feed_url, category, priority, active, description, tags
            FROM blogs
            ORDER BY category, priority DESC
        """)

        rows = cursor.fetchall()

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['blog_name', 'url', 'feed_url', 'category', 'priority', 'active', 'description', 'tags'])

            for row in rows:
                writer.writerow([
                    row[0],  # name
                    row[1],  # url
                    row[2] or '',  # feed_url
                    row[3],  # category
                    row[4],  # priority
                    'true' if row[5] else 'false',  # active
                    row[6] or '',  # description
                    row[7] or ''   # tags
                ])

        conn.close()
        print(f"✅ CSV 내보내기 완료: {output_path} ({len(rows)}개)")

    def list_blogs(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """블로그 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM blogs WHERE 1=1"
        params = []

        if active_only:
            query += " AND active = ?"
            params.append(True)

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY category, priority DESC"

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        blogs = []
        for row in rows:
            blogs.append(dict(zip(columns, row)))

        conn.close()
        return blogs

    def get_stats(self) -> Dict:
        """통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 전체 통계
        cursor.execute("SELECT COUNT(*) FROM blogs")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blogs WHERE active = TRUE")
        active = cursor.fetchone()[0]

        # 카테고리별 통계
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM blogs
            WHERE active = TRUE
            GROUP BY category
            ORDER BY count DESC
        """)
        by_category = dict(cursor.fetchall())

        # 우선순위별 통계
        cursor.execute("""
            SELECT priority, COUNT(*) as count
            FROM blogs
            WHERE active = TRUE
            GROUP BY priority
        """)
        by_priority = dict(cursor.fetchall())

        conn.close()

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_category': by_category,
            'by_priority': by_priority
        }

    def validate_feeds(self, verbose: bool = False) -> Dict:
        """RSS 피드 유효성 검사"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, feed_url FROM blogs WHERE active = TRUE AND feed_url IS NOT NULL")
        blogs = cursor.fetchall()

        results = {
            'valid': [],
            'invalid': [],
            'no_feed': []
        }

        for blog_id, name, feed_url in blogs:
            if not feed_url:
                results['no_feed'].append(name)
                continue

            try:
                response = requests.get(feed_url, timeout=10)
                if response.status_code == 200:
                    results['valid'].append(name)
                    if verbose:
                        print(f"✅ {name}: OK")
                else:
                    results['invalid'].append((name, f"HTTP {response.status_code}"))
                    if verbose:
                        print(f"❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                results['invalid'].append((name, str(e)))
                if verbose:
                    print(f"❌ {name}: {str(e)}")

        conn.close()
        return results

    def print_summary(self):
        """요약 정보 출력"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("📊 블로그 관리 현황")
        print("="*60)
        print(f"전체 블로그: {stats['total']}개")
        print(f"활성화: {stats['active']}개 | 비활성화: {stats['inactive']}개")
        print()
        print("카테고리별:")
        for cat, count in stats['by_category'].items():
            print(f"  - {cat}: {count}개")
        print()
        print("우선순위별:")
        for pri, count in stats['by_priority'].items():
            print(f"  - {pri}: {count}개")
        print("="*60 + "\n")

    def get_post_stats(self) -> Dict:
        """포스트 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 전체 포스트 수
        cursor.execute("SELECT COUNT(*) FROM posts")
        total = cursor.fetchone()[0]

        # 오늘 수집된 포스트
        cursor.execute("SELECT COUNT(*) FROM posts WHERE DATE(scraped_at) = DATE('now')")
        today = cursor.fetchone()[0]

        # 블로그별 포스트 수
        cursor.execute("""
            SELECT b.name, COUNT(p.id) as count
            FROM blogs b
            LEFT JOIN posts p ON b.id = p.blog_id
            GROUP BY b.id, b.name
            ORDER BY count DESC
        """)
        by_blog = dict(cursor.fetchall())

        conn.close()

        return {
            'total_posts': total,
            'posts_today': today,
            'by_blog': by_blog
        }

    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """최근 포스트 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.title, p.url, p.summary, p.published_date,
                   p.scraped_at, b.name as blog_name, b.category
            FROM posts p
            JOIN blogs b ON p.blog_id = b.id
            ORDER BY p.scraped_at DESC
            LIMIT ?
        """, (limit,))

        columns = ['id', 'title', 'url', 'summary', 'published_date', 'scraped_at', 'blog_name', 'category']
        rows = cursor.fetchall()

        posts = []
        for row in rows:
            posts.append(dict(zip(columns, row)))

        conn.close()
        return posts

    def print_post_stats(self):
        """포스트 통계 출력"""
        stats = self.get_post_stats()

        print("\n" + "="*60)
        print("📝 포스트 수집 현황")
        print("="*60)
        print(f"전체 포스트: {stats['total_posts']}개")
        print(f"오늘 수집: {stats['posts_today']}개")
        print()
        print("블로그별 포스트 수:")
        for blog, count in stats['by_blog'].items():
            print(f"  - {blog}: {count}개")
        print("="*60 + "\n")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='블로그 리스트 관리 도구')
    parser.add_argument('action', choices=['init', 'load', 'export', 'list', 'stats', 'validate', 'post-stats', 'recent-posts'],
                       help='실행할 작업')
    parser.add_argument('--csv', help='CSV 파일 경로')
    parser.add_argument('--category', help='카테고리 필터')
    parser.add_argument('--all', action='store_true', help='비활성 블로그도 포함')
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 출력')
    parser.add_argument('--limit', type=int, default=10, help='포스트 개수 제한')

    args = parser.parse_args()

    manager = BlogManager()

    if args.action == 'init':
        print("✅ 데이터베이스 초기화 완료")

    elif args.action == 'load':
        if not args.csv:
            print("❌ --csv 옵션으로 CSV 파일을 지정해주세요")
            return
        manager.load_from_csv(args.csv)
        manager.print_summary()

    elif args.action == 'export':
        output = args.csv or 'blogs_export.csv'
        manager.export_to_csv(output)

    elif args.action == 'list':
        blogs = manager.list_blogs(
            category=args.category,
            active_only=not args.all
        )

        for blog in blogs:
            status = "🟢" if blog['active'] else "🔴"
            print(f"{status} [{blog['category']}] {blog['name']}")
            if args.verbose:
                print(f"   URL: {blog['url']}")
                print(f"   Feed: {blog['feed_url'] or 'N/A'}")
                print(f"   Priority: {blog['priority']}")
                print()

    elif args.action == 'stats':
        manager.print_summary()

    elif args.action == 'validate':
        print("🔍 RSS 피드 유효성 검사 중...\n")
        results = manager.validate_feeds(verbose=args.verbose)

        print(f"\n✅ 유효: {len(results['valid'])}개")
        print(f"❌ 무효: {len(results['invalid'])}개")
        print(f"⚠️  피드 없음: {len(results['no_feed'])}개")

        if results['invalid'] and not args.verbose:
            print("\n무효한 피드:")
            for name, error in results['invalid']:
                print(f"  - {name}: {error}")

    elif args.action == 'post-stats':
        manager.print_post_stats()

    elif args.action == 'recent-posts':
        posts = manager.get_recent_posts(limit=args.limit)

        if not posts:
            print("📭 수집된 포스트가 없습니다.")
            return

        print(f"\n📰 최근 포스트 {len(posts)}개\n")
        for post in posts:
            print(f"[{post['category']}] {post['title']}")
            print(f"   블로그: {post['blog_name']}")
            if post['summary']:
                summary = post['summary'][:100] + ('...' if len(post['summary']) > 100 else '')
                print(f"   요약: {summary}")
            print(f"   URL: {post['url']}")
            print()


if __name__ == '__main__':
    main()
