# 블로그 애그리게이터 프로젝트 구조 📁

## 📊 전체 구조 개요

```
blog-aggregator/
├── 📱 Core Application (핵심 앱)
│   ├── app_v2.py              # 웹 대시보드 (FastAPI)
│   ├── blog_crawler_parallel.py  # 병렬 크롤러 (메인)
│   ├── blog_manager.py        # 블로그 관리
│   ├── blog_auto_tagger.py    # 자동 태깅
│   ├── email_digest.py        # 이메일 다이제스트
│   ├── db_config.py           # DB 연결 관리
│   └── migrate_to_postgres.py # DB 마이그레이션
│
├── 📚 docs/ (문서)
│   ├── README_*.md            # 기능별 가이드
│   ├── blog_sources.md        # 블로그 소스 목록
│   ├── dbeaver_*.md           # DBeaver 연결 가이드
│   └── 블로그_애그리게이션_요건정의서.md
│
├── 💾 data/ (데이터 파일)
│   ├── blogs_list.csv         # 메인 블로그 목록 (35개)
│   ├── analyzed_blogs.csv     # 분석 완료 블로그
│   └── *.txt, *.csv           # 기타 데이터
│
├── 💿 Database (데이터베이스)
│   └── blogs.db               # SQLite 데이터베이스
│
├── 🔧 config/ (설정 파일)
│   ├── schema_postgres.sql    # PostgreSQL 스키마
│   ├── .env.example           # 환경 변수 예시
│   └── com.blog.crawler.plist # macOS 스케줄러
│
├── 🚀 scripts/ (실행 스크립트)
│   ├── setup_postgres.sh      # PostgreSQL 설정
│   ├── setup_scheduler.sh     # 스케줄러 설정
│   └── quick_setup.sh         # 빠른 설정
│
├── 💾 backups/ (백업)
│   ├── blogs_backup_*.db      # DB 백업
│   └── digest_*.html          # 다이제스트 백업
│
├── 📦 legacy/ (레거시 코드)
│   ├── app.py                 # 구버전 앱
│   └── blog_crawler.py        # 순차 크롤러 (구버전)
│
└── 📄 Configuration Files (루트 설정)
    ├── README.md              # 프로젝트 메인 README
    ├── requirements.txt       # Python 패키지
    ├── .gitignore             # Git 제외 파일
    └── .env                   # 환경 변수 (생성 필요)
```

---

## 📱 Core Application (핵심 애플리케이션)

### 1. **app_v2.py**
**웹 대시보드 (FastAPI 기반)**

```python
# 실행 방법
python app_v2.py
# → http://localhost:8000
```

**주요 기능**:
- 📊 포스트 목록 및 필터링
- 🔖 북마크 기능
- ✅ 읽음 표시
- 🌙 다크모드
- 📈 통계 대시보드

**API 엔드포인트**:
- `GET /api/posts` - 포스트 목록
- `GET /api/blogs` - 블로그 목록
- `POST /api/bookmarks/{id}` - 북마크 추가
- `POST /api/read/{id}` - 읽음 표시

---

### 2. **blog_crawler_parallel.py** ⚡
**병렬 RSS 크롤러 (메인 크롤러)**

```bash
# 기본 실행
python blog_crawler_parallel.py --limit 10

# 고급 옵션
python blog_crawler_parallel.py --limit 20 --workers 15 --verbose
```

**특징**:
- 🚀 ThreadPoolExecutor 사용
- ⚡ 10-20배 빠른 속도
- 🔒 스레드 안전 DB 처리
- 📊 실시간 진행 상황

**성능**:
- 35개 블로그 → 2.2초
- 평균 0.06초/블로그

---

### 3. **blog_manager.py**
**블로그 및 DB 관리**

```bash
# 블로그 목록
python blog_manager.py list

# CSV 로드
python blog_manager.py load --csv analyzed_blogs.csv

# 통계
python blog_manager.py post-stats

# 최근 포스트
python blog_manager.py recent-posts --limit 20
```

**기능**:
- 블로그 CRUD
- CSV import/export
- 데이터베이스 초기화
- 통계 조회

---

### 4. **blog_auto_tagger.py**
**블로그 자동 분석 및 태깅**

```bash
# 단일 URL
python blog_auto_tagger.py https://blog.example.com

# 파일에서 읽기
python blog_auto_tagger.py --file data/blogs_list.csv

# 출력 파일 지정
python blog_auto_tagger.py --file input.csv --output result.csv
```

**자동 추출**:
- 📝 블로그 이름
- 🔗 RSS 피드 URL
- 🏷️ 카테고리 (ml, art, tech, data, essay)
- 🔖 태그 (상위 5개)

---

### 5. **email_digest.py**
**이메일 다이제스트 생성/전송**

```bash
# HTML 미리보기
python email_digest.py --days 1 --preview

# 이메일 전송
python email_digest.py --days 7 \
  --send \
  --to-email your@email.com \
  --from-email smtp@gmail.com \
  --password app_password
```

**기능**:
- 📧 HTML 이메일 생성
- 📊 카테고리별 통계
- 🎨 아름다운 디자인
- 📅 일간/주간 다이제스트

---

### 6. **db_config.py**
**데이터베이스 추상화 레이어**

```python
from db_config import get_db_config

# 자동으로 SQLite 또는 PostgreSQL 선택
config = get_db_config()

# 쿼리 실행
results = config.execute_query("SELECT * FROM blogs LIMIT 10")
```

**지원 DB**:
- SQLite (기본)
- PostgreSQL (환경 변수로 전환)

---

### 7. **migrate_to_postgres.py**
**SQLite → PostgreSQL 마이그레이션**

```bash
python migrate_to_postgres.py \
  --sqlite blogs.db \
  --pg-db blog_aggregator \
  --pg-user postgres \
  --drop
```

**마이그레이션 항목**:
- 블로그 (35개)
- 포스트 (341개)
- 북마크
- 읽음 표시

---

## 📚 Documentation (docs/)

| 파일 | 내용 |
|------|------|
| **README_blog_manager.md** | 블로그 관리 가이드 |
| **README_crawler.md** | 크롤러 사용법 |
| **README_auto_tagger.md** | 자동 태거 가이드 |
| **README_scheduler.md** | 자동 스케줄링 설정 |
| **README_postgresql.md** | PostgreSQL 업그레이드 |
| **dbeaver_connection_sqlite.md** | DBeaver SQLite 연결 |
| **dbeaver_connection_postgres.md** | DBeaver PostgreSQL 연결 |
| **blog_sources.md** | 추천 블로그 목록 |
| **블로그_애그리게이션_요건정의서.md** | 초기 요구사항 정의 |

---

## 💾 Data Files (data/)

### 메인 데이터 파일

| 파일 | 용도 | 크기 |
|------|------|------|
| **blogs_list.csv** | 현재 사용 중인 블로그 목록 | 35개 |
| **analyzed_blogs.csv** | 자동 분석 완료 결과 | 35개 |
| **blogs_template.csv** | 빈 템플릿 | - |

### 아카이브

- `quick_100_blogs.txt` - 100개 블로그 URL 목록
- `quick_100_analyzed.csv` - 100개 블로그 분석 결과
- `blog_urls.txt` - 추가 URL 모음
- `test_urls.txt` - 테스트용 URL

---

## 💿 Database

### **blogs.db** (SQLite)
**현재 데이터**:
- 블로그: 35개
- 포스트: 341개
- 크기: ~120KB

**테이블 구조**:
```sql
blogs         (블로그 정보)
posts         (포스트 내용)
bookmarks     (북마크)
read_posts    (읽음 표시)
```

---

## 🔧 Configuration (config/)

### 1. **schema_postgres.sql**
PostgreSQL 데이터베이스 스키마
- 테이블 정의
- 인덱스 (7개)
- 뷰 (blog_stats, recent_posts)
- 트리거 (auto update_at)

### 2. **.env.example**
환경 변수 템플릿

```bash
# 사용 방법
cp config/.env.example .env
# .env 파일 편집
```

### 3. **com.blog.crawler.plist**
macOS launchd 스케줄러 설정
- 매일 오전 9시, 오후 6시 실행

---

## 🚀 Scripts (scripts/)

### 1. **setup_postgres.sh**
PostgreSQL 전체 설정 자동화

```bash
./scripts/setup_postgres.sh
```

**수행 작업**:
1. PostgreSQL 설치 확인
2. 데이터베이스 생성
3. .env 파일 생성
4. Python 패키지 설치
5. 데이터 마이그레이션

### 2. **setup_scheduler.sh**
자동 스케줄러 설정

```bash
./scripts/setup_scheduler.sh
```

### 3. **quick_setup.sh**
전체 프로젝트 빠른 설정

```bash
./scripts/quick_setup.sh
```

---

## 💾 Backups (backups/)

### 자동 백업 파일
- `blogs_backup_111.db` - 이전 DB 백업 (111개 블로그)
- `digest_*.html` - 이메일 다이제스트 백업

### 백업 정책
```bash
# 수동 백업
cp blogs.db backups/blogs_$(date +%Y%m%d).db

# 자동 백업 (cron)
0 3 * * * cp /path/blogs.db /path/backups/blogs_$(date +\%Y\%m\%d).db
```

---

## 📦 Legacy (legacy/)

구버전 파일 (사용 중지):
- `app.py` - 구 대시보드
- `blog_crawler.py` - 순차 크롤러 (느림)

**새 버전 사용 권장**:
- `app_v2.py` ✅
- `blog_crawler_parallel.py` ✅

---

## 📄 Root Configuration Files

### **README.md**
프로젝트 메인 문서

### **requirements.txt**
Python 패키지 의존성

```bash
pip install -r requirements.txt
```

**주요 패키지**:
- FastAPI (웹 프레임워크)
- feedparser (RSS 파싱)
- psycopg2-binary (PostgreSQL)
- beautifulsoup4 (HTML 파싱)

### **.gitignore**
Git 제외 파일 목록

**제외 항목**:
- `.env` (비밀번호 포함)
- `*.db` (데이터베이스)
- `__pycache__/`
- `*.pyc`

---

## 🎯 주요 워크플로우

### 1. **초기 설정**
```bash
# 자동 설정
./scripts/quick_setup.sh

# 블로그 추가
python blog_auto_tagger.py --file data/blogs_list.csv
python blog_manager.py load --csv data/analyzed_blogs.csv
```

### 2. **일상 사용**
```bash
# 포스트 수집 (2초)
python blog_crawler_parallel.py --limit 10

# 웹 대시보드 실행
python app_v2.py
# → http://localhost:8000
```

### 3. **데이터 관리**
```bash
# 통계 확인
python blog_manager.py post-stats

# 최근 포스트
python blog_manager.py recent-posts --limit 20

# 백업
cp blogs.db backups/blogs_$(date +%Y%m%d).db
```

---

## 📊 파일 크기 및 통계

| 카테고리 | 파일 수 | 총 크기 |
|---------|--------|---------|
| Core Apps | 7개 | ~100KB |
| Documentation | 10개 | ~200KB |
| Data Files | 8개 | ~50KB |
| Database | 1개 | ~120KB |
| Backups | 2개 | ~2MB |
| Scripts | 3개 | ~20KB |

**총 프로젝트 크기**: ~2.5MB

---

## 🔍 파일 검색 팁

### 특정 파일 찾기
```bash
# 이름으로 검색
find . -name "*crawler*"

# 타입별 검색
find . -name "*.py"  # Python 파일
find . -name "*.md"  # 문서 파일
find . -name "*.csv" # 데이터 파일
```

### 내용으로 검색
```bash
# 코드에서 검색
grep -r "def crawl" *.py

# 문서에서 검색
grep -r "PostgreSQL" docs/
```

---

## 🧹 정리 및 유지보수

### 임시 파일 정리
```bash
# Python 캐시 삭제
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# 오래된 백업 삭제 (30일 이상)
find backups/ -name "*.db" -mtime +30 -delete
```

### 디스크 사용량 확인
```bash
# 디렉토리별 크기
du -sh *

# 큰 파일 찾기
find . -type f -size +1M
```

---

## 📱 다음 단계

1. **문서 읽기**: [README.md](README.md) 시작
2. **설정**: `./scripts/quick_setup.sh`
3. **크롤링**: `python blog_crawler_parallel.py --limit 10`
4. **웹 확인**: `python app_v2.py`

---

## 💡 팁

- 📚 문서는 `docs/` 폴더에서 찾기
- 🔧 설정 파일은 `config/`에 보관
- 💾 데이터는 정기적으로 백업
- 🚀 새 기능은 메인 앱 파일 수정

**프로젝트 구조가 깔끔하게 정리되었습니다!** 🎉
