# 블로그 애그리게이션 플랫폼 📚

100개 블로그의 콘텐츠를 자동으로 수집하고 요약하여 한 곳에서 확인하는 개인용 큐레이션 플랫폼

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## ✨ 주요 기능

- 🔄 **자동 크롤링**: RSS 피드 기반 포스트 자동 수집
- 🤖 **자동 요약**: AI 또는 키워드 기반 200자 요약
- 🏷️ **자동 태그 생성**: 블로그 URL만 입력하면 자동으로 태그, 카테고리, RSS 피드 추출
- 🎨 **웹 대시보드**: 타임라인 뷰, 검색, 필터링
- 📊 **통계**: 블로그별, 카테고리별 포스트 현황

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd blog-aggregator

# 패키지 설치
pip install -r requirements.txt
```

### 2. 블로그 추가

**방법 A: 자동 태그 생성** (추천)
```bash
# URL만 입력하면 자동으로 모든 정보 추출
python blog_auto_tagger.py https://openai.com/blog https://techcrunch.com

# 또는 파일에서 일괄 처리
python blog_auto_tagger.py --file blog_urls.txt

# DB에 로드
python blog_manager.py load --csv analyzed_blogs.csv
```

**방법 B: CSV 직접 편집**
```bash
# blogs_list.csv 편집 후
python blog_manager.py load --csv blogs_list.csv
```

### 3. 크롤링 실행

```bash
# 모든 블로그 크롤링
python blog_crawler.py

# 특정 블로그만
python blog_crawler.py --blog-id 1 --verbose

# 포스트 수 제한
python blog_crawler.py --limit 5
```

### 4. 웹 대시보드 실행

```bash
python app.py
```

브라우저에서 http://localhost:8000 접속!

## 📁 프로젝트 구조

```
blog-aggregator/
├── blog_manager.py              # 블로그 관리 시스템
├── blog_auto_tagger.py          # 자동 태그 생성기
├── blog_crawler.py              # RSS 크롤러
├── app.py                       # 웹 대시보드
├── blogs.db                     # SQLite 데이터베이스
├── blogs_list.csv               # 블로그 목록 예시
├── requirements.txt             # 필수 패키지
├── 블로그_애그리게이션_요건정의서.md
├── README_blog_manager.md       # 블로그 관리 가이드
├── README_auto_tagger.md        # 자동 태그 생성 가이드
└── README_crawler.md            # 크롤러 사용 가이드
```

## 🎯 사용 시나리오

### 시나리오 1: 처음 시작 (100개 블로그 추가)

```bash
# 1. 관심 블로그 URL 수집 (blog_urls.txt에 저장)
# 2. 자동 분석
python blog_auto_tagger.py --file blog_urls.txt

# 3. DB에 로드
python blog_manager.py load --csv analyzed_blogs.csv

# 4. 크롤링
python blog_crawler.py --limit 10

# 5. 대시보드 실행
python app.py
```

**예상 시간**: 30분

### 시나리오 2: 매일 새 글 확인

```bash
# 크롤링 (새 포스트만 자동 수집)
python blog_crawler.py

# 결과 확인
python blog_manager.py recent-posts --limit 20
```

### 시나리오 3: 정기 자동화

```bash
# cron 설정 (매일 오전 9시)
crontab -e
# 0 9 * * * cd /path/to/project && python blog_crawler.py
```

## 📊 현재 상태

- ✅ 11개 블로그 등록
- ✅ 50개 포스트 수집
- ✅ 자동 요약 생성
- ✅ 웹 대시보드 완성

## 🛠 주요 명령어

### 블로그 관리
```bash
python blog_manager.py list              # 블로그 목록
python blog_manager.py stats             # 블로그 통계
python blog_manager.py validate          # RSS 피드 검증
```

### 포스트 관리
```bash
python blog_manager.py post-stats        # 포스트 통계
python blog_manager.py recent-posts      # 최근 포스트
```

### 크롤링
```bash
python blog_crawler.py                   # 전체 크롤링
python blog_crawler.py --verbose         # 상세 출력
python blog_crawler.py --blog-id 1       # 특정 블로그만
```

### 웹 대시보드
```bash
python app.py                            # 서버 실행
# http://localhost:8000 접속
# http://localhost:8000/docs - API 문서
```

## 🎨 기능 상세

### 1. 자동 태그 생성
블로그 URL만 입력하면 자동으로:
- 📝 블로그 이름 추출
- 🔗 RSS 피드 URL 자동 발견
- 🏷️ 카테고리 자동 분류 (ml, art, tech, data, essay)
- 🔖 태그 자동 생성 (최대 5개)
- 📄 설명 추출

### 2. RSS 크롤러
- ✅ 네이버 블로그, 브런치 등 다양한 플랫폼 지원
- ✅ 중복 자동 제거
- ✅ Rate limiting (2초 간격)
- ✅ 에러 처리 (개별 실패해도 전체 계속)

### 3. 자동 요약
- 현재: HTML 제거 후 200자 추출
- 향후: OpenAI/Claude API 연동 가능

### 4. 웹 대시보드
- 📱 반응형 디자인
- 🔍 실시간 검색
- 📂 카테고리/블로그 필터
- 📄 페이지네이션
- 📊 통계 대시보드

## 🔮 향후 계획 (Phase 2)

- [ ] **AI 요약**: OpenAI GPT-4-mini 연동
- [ ] **자동 스케줄링**: Celery + Redis
- [ ] **이메일 다이제스트**: 주간 요약 메일
- [ ] **모바일 앱**: PWA 또는 React Native
- [ ] **소셜 기능**: 북마크, 공유, 추천

## 📖 문서

- [블로그 관리 가이드](README_blog_manager.md)
- [자동 태그 생성 가이드](README_auto_tagger.md)
- [크롤러 사용 가이드](README_crawler.md)
- [요건정의서](블로그_애그리게이션_요건정의서.md)

## 🤝 기여

개인 프로젝트이지만 제안이나 이슈는 환영합니다!

## 📝 라이선스

MIT License

## 💡 팁

### 블로그 100개 빠르게 채우기
```bash
# 1. 관심 주제로 블로그 검색
#    "best machine learning blogs 2024"
#    "top design blogs korea"

# 2. blog_urls.txt에 URL 복붙 (100개)

# 3. 자동 분석 실행 (5분 소요)
python blog_auto_tagger.py --file blog_urls.txt

# 4. 완료!
```

### RSS 피드 찾기
대부분의 블로그는 다음 패턴:
- `https://example.com/feed`
- `https://example.com/rss`
- `https://example.com/atom.xml`

자동 탐지 안 되면 브라우저에서 페이지 소스 보기 → "rss" 검색

### 성능 최적화
- SQLite → PostgreSQL (100개 이상 블로그)
- 로컬 실행 → 클라우드 (항상 켜진 서버)
- 동기 → 비동기 (Celery)

## 🔧 문제 해결

### "No module named 'feedparser'"
```bash
pip install -r requirements.txt
```

### "Database is locked"
```bash
# 다른 프로세스가 DB 사용 중
# 크롤러나 웹서버 중 하나만 실행
```

### 포스트가 수집 안 됨
```bash
# RSS 피드 검증
python blog_manager.py validate --verbose

# 특정 블로그 상세 확인
python blog_crawler.py --blog-id 1 --verbose
```

## 📞 연락

궁금한 점이나 버그 리포트는 이슈로 등록해주세요!

---

**Made with ❤️ and Claude Code**
