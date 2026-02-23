"""
블로그 자동 태그 생성기
URL만 입력하면 태그, 카테고리, RSS 피드 등을 자동으로 추출합니다.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from collections import Counter
import json


class BlogAutoTagger:
    """블로그 자동 분석 및 태그 생성"""

    def __init__(self, use_ai: bool = False, api_key: str = None):
        self.use_ai = use_ai
        self.api_key = api_key

        # 카테고리 키워드 사전
        self.category_keywords = {
            'ml': [
                'machine learning', 'deep learning', 'neural network', 'ai', 'artificial intelligence',
                'tensorflow', 'pytorch', 'model', 'training', 'dataset', 'algorithm',
                '머신러닝', '딥러닝', '인공지능', '신경망', '모델', '학습', '알고리즘'
            ],
            'art': [
                'art', 'design', 'creative', 'illustration', 'painting', 'drawing', 'visual',
                'artist', 'gallery', 'exhibition', 'photography', 'graphic',
                '아트', '디자인', '예술', '일러스트', '그림', '창작', '전시', '사진'
            ],
            'tech': [
                'technology', 'software', 'programming', 'development', 'code', 'web', 'app',
                'startup', 'innovation', 'digital', 'tech', 'developer',
                '기술', '소프트웨어', '프로그래밍', '개발', '코딩', '스타트업', '디지털'
            ],
            'data': [
                'data', 'analytics', 'statistics', 'visualization', 'analysis', 'dashboard',
                'sql', 'database', 'big data', 'insight',
                '데이터', '분석', '통계', '시각화', '데이터베이스', '인사이트'
            ],
            'essay': [
                'essay', 'thought', 'opinion', 'writing', 'story', 'life', 'philosophy',
                'personal', 'reflection', 'experience',
                '에세이', '생각', '글', '이야기', '철학', '경험', '일상'
            ]
        }

        # 일반적인 불용어 (태그에서 제외)
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'about', 'more', 'new', 'how', 'what', 'when', 'where', 'why', 'this',
            'that', 'these', 'those', 'blog', 'post', 'article',
            '그', '이', '저', '것', '수', '등', '및', '더', '블로그', '포스트'
        }

    def analyze_blog(self, url: str) -> Dict:
        """블로그 URL 분석하여 모든 정보 추출"""
        print(f"🔍 분석 중: {url}")

        try:
            # 웹페이지 가져오기
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 각종 정보 추출
            blog_name = self._extract_blog_name(soup, url)
            description = self._extract_description(soup)
            feed_url = self._find_feed_url(soup, url)
            text_content = self._extract_text_content(soup)

            # 태그 및 카테고리 분석
            if self.use_ai and self.api_key:
                tags, category = self._analyze_with_ai(text_content, blog_name, description)
            else:
                tags = self._extract_tags_keyword_based(text_content)
                category = self._classify_category(text_content)

            result = {
                'blog_name': blog_name,
                'url': url,
                'feed_url': feed_url,
                'category': category,
                'priority': 'medium',
                'active': 'true',
                'description': description[:200] if description else '',
                'tags': ','.join(tags[:5]),  # 최대 5개
                'confidence': 'ai' if self.use_ai else 'keyword'
            }

            print(f"✅ 완료: {blog_name}")
            return result

        except Exception as e:
            print(f"❌ 오류: {str(e)}")
            return {
                'blog_name': urlparse(url).netloc,
                'url': url,
                'feed_url': '',
                'category': 'other',
                'priority': 'medium',
                'active': 'true',
                'description': f'자동 분석 실패: {str(e)}',
                'tags': '',
                'confidence': 'failed'
            }

    def _extract_blog_name(self, soup: BeautifulSoup, url: str) -> str:
        """블로그 이름 추출"""
        # 1. <title> 태그
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            # 일반적인 구분자로 분리
            for sep in [' | ', ' - ', ' :: ', ' — ']:
                if sep in title:
                    return title.split(sep)[-1].strip()
            return title

        # 2. Open Graph
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            return og_site_name['content'].strip()

        # 3. 도메인 이름
        domain = urlparse(url).netloc
        return domain.replace('www.', '').split('.')[0].title()

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """블로그 설명 추출"""
        # 1. Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        # 2. Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        # 3. 첫 번째 단락
        first_p = soup.find('p')
        if first_p:
            return first_p.get_text().strip()[:200]

        return ''

    def _find_feed_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """RSS/Atom 피드 URL 찾기"""
        # 1. <link> 태그에서 찾기
        feed_links = soup.find_all('link', type=['application/rss+xml', 'application/atom+xml'])
        if feed_links:
            href = feed_links[0].get('href')
            if href:
                return urljoin(base_url, href)

        # 2. 일반적인 피드 경로 시도
        common_feeds = [
            '/feed',
            '/rss',
            '/feed.xml',
            '/rss.xml',
            '/atom.xml',
            '/blog/feed',
            '/feeds/posts/default'  # Blogger
        ]

        for feed_path in common_feeds:
            feed_url = urljoin(base_url, feed_path)
            try:
                response = requests.head(feed_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'xml' in content_type or 'rss' in content_type or 'atom' in content_type:
                        return feed_url
            except:
                continue

        return None

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """페이지에서 텍스트 콘텐츠 추출"""
        # 스크립트, 스타일 제거
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        # 본문 추출 (일반적인 본문 태그들)
        main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'(content|main|post|article)', re.I))

        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)

        # 공백 정리
        text = re.sub(r'\s+', ' ', text)
        return text[:5000]  # 처음 5000자만

    def _extract_tags_keyword_based(self, text: str) -> List[str]:
        """키워드 기반 태그 추출"""
        # 소문자 변환
        text_lower = text.lower()

        # 단어 추출 (2-20자 단어만)
        words = re.findall(r'\b[a-z가-힣]{2,20}\b', text_lower)

        # 불용어 제거
        words = [w for w in words if w not in self.stopwords]

        # 빈도수 계산
        word_freq = Counter(words)

        # 상위 빈출 단어
        common_words = [word for word, count in word_freq.most_common(20)]

        # 카테고리 키워드와 매칭되는 것 우선
        matched_tags = []
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower and keyword not in matched_tags:
                    matched_tags.append(keyword.replace(' ', '-'))

        # 빈출 단어 추가 (최대 10개)
        for word in common_words:
            if word not in matched_tags and len(word) > 2:
                matched_tags.append(word)
            if len(matched_tags) >= 10:
                break

        return matched_tags[:10]

    def _classify_category(self, text: str) -> str:
        """텍스트 기반 카테고리 분류"""
        text_lower = text.lower()

        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            scores[category] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'other'

    def _analyze_with_ai(self, text: str, blog_name: str, description: str) -> tuple:
        """AI 기반 분석 (OpenAI API)"""
        try:
            import openai
            openai.api_key = self.api_key

            prompt = f"""
다음 블로그를 분석해서 적절한 태그 5개와 카테고리 1개를 추출해주세요.

블로그 이름: {blog_name}
설명: {description}
콘텐츠 샘플: {text[:1500]}

카테고리는 다음 중 하나를 선택: ml, art, tech, data, essay, other

JSON 형식으로 답변:
{{
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "category": "ml"
}}
"""

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            return result['tags'], result['category']

        except Exception as e:
            print(f"⚠️  AI 분석 실패, 키워드 기반으로 전환: {str(e)}")
            return self._extract_tags_keyword_based(text), self._classify_category(text)


def analyze_single_blog(url: str, use_ai: bool = False, api_key: str = None):
    """단일 블로그 분석"""
    tagger = BlogAutoTagger(use_ai=use_ai, api_key=api_key)
    result = tagger.analyze_blog(url)

    print("\n" + "="*60)
    print("📊 분석 결과")
    print("="*60)
    for key, value in result.items():
        if key != 'confidence':
            print(f"{key:15s}: {value}")
    print("="*60 + "\n")

    return result


def analyze_multiple_blogs(urls: List[str], output_csv: str = 'analyzed_blogs.csv', use_ai: bool = False, api_key: str = None):
    """여러 블로그 일괄 분석"""
    import csv

    tagger = BlogAutoTagger(use_ai=use_ai, api_key=api_key)
    results = []

    print(f"\n🚀 {len(urls)}개 블로그 분석 시작...\n")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] ", end='')
        result = tagger.analyze_blog(url.strip())
        results.append(result)
        print()

    # CSV 저장
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['blog_name', 'url', 'feed_url', 'category', 'priority', 'active', 'description', 'tags']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({k: result[k] for k in fieldnames})

    print(f"\n✅ 완료! {len(results)}개 블로그 정보가 {output_csv}에 저장되었습니다.")
    print(f"\n다음 명령으로 DB에 로드:")
    print(f"  python blog_manager.py load --csv {output_csv}")

    return results


def main():
    """메인 실행"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='블로그 자동 태그 생성기')
    parser.add_argument('urls', nargs='*', help='분석할 블로그 URL (여러 개 가능)')
    parser.add_argument('--file', '-f', help='URL 목록 파일 (한 줄에 하나씩)')
    parser.add_argument('--output', '-o', default='analyzed_blogs.csv', help='출력 CSV 파일명')
    parser.add_argument('--ai', action='store_true', help='AI 기반 분석 사용 (OpenAI API 필요)')
    parser.add_argument('--api-key', help='OpenAI API 키')

    args = parser.parse_args()

    # URL 수집
    urls = []

    if args.urls:
        urls.extend(args.urls)

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                urls.extend(file_urls)
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
            sys.exit(1)

    if not urls:
        # 대화형 모드
        print("블로그 자동 태그 생성기")
        print("="*60)
        print("URL을 입력하세요 (여러 개는 Enter로 구분, 완료는 빈 줄):")
        print()

        while True:
            url = input("URL: ").strip()
            if not url:
                break
            urls.append(url)

    if not urls:
        print("❌ URL이 입력되지 않았습니다.")
        sys.exit(1)

    # AI 모드 확인
    use_ai = args.ai
    api_key = args.api_key

    if use_ai and not api_key:
        api_key = input("OpenAI API 키를 입력하세요: ").strip()
        if not api_key:
            print("⚠️  API 키가 없어 키워드 기반으로 진행합니다.")
            use_ai = False

    # 분석 실행
    if len(urls) == 1:
        analyze_single_blog(urls[0], use_ai=use_ai, api_key=api_key)
    else:
        analyze_multiple_blogs(urls, output_csv=args.output, use_ai=use_ai, api_key=api_key)


if __name__ == '__main__':
    main()
