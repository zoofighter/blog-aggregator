# 블로그 리스트 관리 가이드

100개 블로그를 효율적으로 관리하기 위한 도구입니다.

## 📁 파일 구조

```
├── blogs_list.csv          # 예시 블로그 20개 (참고용)
├── blogs_template.csv      # 빈 템플릿 (새 블로그 추가용)
├── blog_manager.py         # 관리 스크립트
└── blogs.db               # SQLite 데이터베이스 (자동 생성)
```

## 🚀 빠른 시작

### 1. CSV 파일에 블로그 추가

`blogs_list.csv` 파일을 열어서 블로그 정보를 입력하세요:

| 컬럼 | 설명 | 예시 |
|------|------|------|
| blog_name | 블로그 이름 | "OpenAI Blog" |
| url | 블로그 URL | https://openai.com/blog |
| feed_url | RSS 피드 URL | https://openai.com/blog/rss |
| category | 카테고리 | ml, art, tech, data, essay |
| priority | 우선순위 | high, medium, low |
| active | 활성화 상태 | true, false |
| description | 설명 | "OpenAI official blog" |
| tags | 태그 (쉼표 구분) | "ai,research,gpt" |

### 2. 데이터베이스에 로드

```bash
# 필요한 라이브러리 설치
pip install requests

# CSV를 데이터베이스로 로드
python blog_manager.py load --csv blogs_list.csv
```

### 3. 통계 확인

```bash
python blog_manager.py stats
```

출력 예시:
```
============================================================
📊 블로그 관리 현황
============================================================
전체 블로그: 100개
활성화: 95개 | 비활성화: 5개

카테고리별:
  - ml: 35개
  - art: 25개
  - tech: 20개
  - data: 15개
  - essay: 5개

우선순위별:
  - high: 30개
  - medium: 50개
  - low: 15개
============================================================
```

## 📝 사용 가이드

### 블로그 목록 보기

```bash
# 모든 활성 블로그
python blog_manager.py list

# 특정 카테고리만
python blog_manager.py list --category ml

# 비활성 블로그도 포함
python blog_manager.py list --all

# 상세 정보 포함
python blog_manager.py list --verbose
```

### CSV로 내보내기

```bash
# 데이터베이스 → CSV
python blog_manager.py export --csv my_blogs.csv
```

### RSS 피드 검증

```bash
# RSS 피드가 정상 작동하는지 확인
python blog_manager.py validate

# 상세 출력
python blog_manager.py validate --verbose
```

## 🎯 100개 블로그 채우기 가이드

### 추천 블로그 카테고리 분배

```yaml
Machine Learning (35개):
  - 연구 블로그: OpenAI, DeepMind, Google AI, Meta AI
  - 실용 튜토리얼: Machine Learning Mastery, Towards Data Science
  - 논문 해설: Distill.pub, Papers With Code
  - 개인 블로그: Andrew Ng, Sebastian Ruder, Andrej Karpathy

Art & Design (25개):
  - 디지털 아트: Creative Applications, Colossal
  - 디자인: Awwwards, Designboom, It's Nice That
  - 일러스트레이션: Illustration Age, Society6 Blog
  - 사진: Fstoppers, PetaPixel

Tech & Programming (20개):
  - 웹 개발: Smashing Magazine, CSS-Tricks, A List Apart
  - 일반 프로그래밍: Martin Fowler, Joel on Software
  - 뉴스: TechCrunch, Hacker News, The Verge

Data Science (15개):
  - 데이터 분석: FiveThirtyEight, FlowingData
  - 시각화: Information is Beautiful, Tableau Blog
  - 통계: Simply Statistics, Statistical Modeling

Essay & Others (5개):
  - 기술 에세이: Paul Graham, Wait But Why
  - 생각/철학: Brain Pickings, Farnam Street
```

### 블로그 발견 방법

1. **검색 엔진**
   ```
   "best machine learning blogs 2024"
   "top art and design blogs"
   "must-read programming blogs"
   ```

2. **큐레이션 사이트**
   - Feedly (인기 피드)
   - Alltop (주제별 블로그)
   - Blogarama

3. **Reddit 커뮤니티**
   - r/MachineLearning
   - r/ArtistLounge
   - r/programming

4. **Medium Publications**
   - Towards Data Science
   - UX Collective
   - Better Programming

### RSS 피드 찾기 팁

대부분의 블로그는 다음 패턴을 따릅니다:

```
https://example.com/feed
https://example.com/rss
https://example.com/atom.xml
https://example.com/feed.xml
https://example.com/blog/feed
```

**자동 탐지 도구:**
- 브라우저 확장: RSS Subscription Extension
- 웹사이트: https://www.feedspot.com (RSS 자동 찾기)

### CSV 채우기 워크플로우

1. **카테고리별로 나눠서 작업**
   ```bash
   # ML 블로그 35개 → blogs_ml.csv
   # Art 블로그 25개 → blogs_art.csv
   # ...
   ```

2. **일괄 추가**
   ```bash
   python blog_manager.py load --csv blogs_ml.csv
   python blog_manager.py load --csv blogs_art.csv
   # 중복은 자동으로 업데이트됨
   ```

3. **검증**
   ```bash
   python blog_manager.py validate
   # 실패한 피드는 수동 확인
   ```

## 🔧 Python 스크립트에서 사용

```python
from blog_manager import BlogManager

# 초기화
manager = BlogManager()

# CSV 로드
manager.load_from_csv('blogs_list.csv')

# 통계
stats = manager.get_stats()
print(f"총 {stats['active']}개 활성 블로그")

# 블로그 목록
ml_blogs = manager.list_blogs(category='ml')
for blog in ml_blogs:
    print(f"{blog['name']}: {blog['feed_url']}")

# 피드 검증
results = manager.validate_feeds()
print(f"유효한 피드: {len(results['valid'])}개")
```

## 📊 엑셀에서 편집하기

CSV 파일을 엑셀에서 열어서 편집할 수 있습니다:

1. **엑셀 열기** → "데이터" → "텍스트에서"
2. 구분 기호: 쉼표
3. 편집 후 **CSV UTF-8로 저장** (중요!)

**주의**: 일반 CSV로 저장하면 한글이 깨질 수 있습니다.

## 🎨 Google Sheets 활용

공동 작업이 필요하면 Google Sheets 사용:

1. Google Sheets에 업로드
2. 팀원과 공유하여 함께 채우기
3. 완료 후 CSV로 다운로드
4. `blog_manager.py load` 실행

## 🚨 주의사항

### 저작권 및 크롤링 정책

1. **robots.txt 확인**
   - 각 블로그의 `https://example.com/robots.txt` 확인
   - Disallow 규칙 준수

2. **크롤링 빈도**
   - 너무 자주 요청하지 않기
   - Rate limiting 설정 (예: 5초 간격)

3. **User-Agent 설정**
   ```python
   headers = {
       'User-Agent': 'PersonalBlogAggregator/1.0 (your@email.com)'
   }
   ```

### 데이터 관리

1. **백업**
   ```bash
   # 정기적으로 백업
   cp blogs.db blogs_backup_$(date +%Y%m%d).db
   python blog_manager.py export --csv blogs_backup.csv
   ```

2. **버전 관리**
   - CSV 파일을 Git에 커밋
   - 변경사항 추적

## 🔄 다음 단계

블로그 리스트가 준비되면:

1. **크롤러 개발** → `crawler.py`
2. **요약 시스템** → `summarizer.py`
3. **웹 인터페이스** → `app.py`

---

## 📞 도움말

### 자주 묻는 질문

**Q: RSS 피드가 없는 블로그는?**
A: feed_url을 비워두세요. 나중에 웹 크롤러로 처리합니다.

**Q: 100개를 꼭 채워야 하나요?**
A: 아니요. 10-20개로 시작해서 점진적으로 늘리는 것을 권장합니다.

**Q: 카테고리를 더 추가하고 싶어요**
A: CSV에 새 카테고리 이름을 자유롭게 추가하세요.

**Q: 블로그가 더 이상 업데이트 안 돼요**
A: active를 false로 변경하고 다시 로드하세요.

---

**작성일**: 2024-02-23
**버전**: 1.0
