# blog_manager.py 완벽 가이드 🔧

## 📋 개요

**blog_manager.py** = 블로그 데이터베이스 관리 도구

### 주요 기능

✅ 데이터베이스 초기화 (테이블 생성)
✅ CSV 파일 로드/내보내기
✅ 블로그 목록 조회
✅ 통계 분석
✅ RSS 피드 검증
✅ 포스트 통계

---

## 🚀 빠른 시작

### 1. 데이터베이스 초기화

```bash
python blog_manager.py init
```

**결과**: `blogs.db` 생성 (4개 테이블)

---

### 2. CSV에서 블로그 로드

```bash
python blog_manager.py load --csv data/blogs_list.csv
```

**결과**:
```
✅ CSV 로드 완료: 35개 추가, 0개 업데이트
```

---

### 3. 블로그 목록 확인

```bash
python blog_manager.py list
```

**결과**:
```
============================================================
📊 블로그 목록 (35개)
============================================================
[1] 요즘IT (tech)
    URL: https://yozm.wishket.com
    RSS: https://yozm.wishket.com/rss
...
```

---

### 4. 통계 확인

```bash
python blog_manager.py stats
```

**결과**:
```
============================================================
📊 블로그 관리 현황
============================================================
전체 블로그: 35개
활성화: 35개 | 비활성화: 0개

카테고리별:
  - other: 25개
  - ml: 4개
  - essay: 4개
============================================================
```

---

## 🏗️ 내부 구조

### 클래스 다이어그램

```python
class BlogManager:
    """블로그 소스 관리 클래스"""

    def __init__(db_path="blogs.db"):
        """초기화 및 DB 생성"""
        self.db_path = db_path
        self.init_database()

    # === 데이터베이스 ===
    def init_database():
        """테이블 생성 및 인덱스 설정"""
        # blogs, posts, bookmarks, read_posts 테이블
        # 성능 최적화 인덱스 5개

    # === CSV 관리 ===
    def load_from_csv(csv_path):
        """CSV → DB 로드"""
        # 중복 체크 후 추가/업데이트

    def export_to_csv(output_path):
        """DB → CSV 내보내기"""

    # === 조회 ===
    def list_blogs(category=None, active_only=True):
        """블로그 목록"""

    def get_stats():
        """블로그 통계"""

    def get_post_stats():
        """포스트 통계"""

    def get_recent_posts(limit=10):
        """최근 포스트"""

    # === 검증 ===
    def validate_feeds(verbose=False):
        """RSS 피드 유효성 검사"""

    # === 출력 ===
    def print_summary():
        """요약 출력"""

    def print_post_stats():
        """포스트 통계 출력"""
```

---

## 📊 데이터베이스 스키마

### 1. blogs 테이블

```sql
CREATE TABLE blogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- 블로그 이름
    url TEXT NOT NULL,                -- 블로그 URL
    feed_url TEXT,                    -- RSS 피드 URL
    category TEXT,                    -- 카테고리 (ml, art, tech, data, essay)
    priority TEXT DEFAULT 'medium',   -- 우선순위 (high, medium, low)
    active BOOLEAN DEFAULT TRUE,      -- 활성화 여부
    description TEXT,                 -- 설명
    tags TEXT,                        -- 태그 (쉼표 구분)
    crawl_interval INTEGER DEFAULT 180, -- 크롤링 간격 (분)
    last_crawled TIMESTAMP,           -- 마지막 크롤링 시각
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 2. posts 테이블

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blog_id INTEGER NOT NULL,         -- 블로그 ID (FK)
    title TEXT NOT NULL,              -- 제목
    url TEXT UNIQUE NOT NULL,         -- 포스트 URL
    author TEXT,                      -- 작성자
    published_date TIMESTAMP,         -- 발행일
    content TEXT,                     -- 본문
    summary TEXT,                     -- 요약
    image_url TEXT,                   -- 대표 이미지
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blog_id) REFERENCES blogs(id)
)
```

### 3. bookmarks 테이블

```sql
CREATE TABLE bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,         -- 포스트 ID (FK)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    UNIQUE(post_id)
)
```

### 4. read_posts 테이블

```sql
CREATE TABLE read_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,         -- 포스트 ID (FK)
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    UNIQUE(post_id)
)
```

### 인덱스 (성능 최적화)

```sql
CREATE INDEX idx_posts_blog_id ON posts(blog_id);
CREATE INDEX idx_posts_scraped_at ON posts(scraped_at DESC);
CREATE INDEX idx_posts_published_date ON posts(published_date DESC);
CREATE INDEX idx_blogs_category ON blogs(category);
CREATE INDEX idx_blogs_active ON blogs(active);
```

---

## 🎯 주요 명령어

### init - 데이터베이스 초기화

```bash
python blog_manager.py init
```

**용도**: 새로운 데이터베이스 생성
**결과**: `blogs.db` 파일 생성

---

### load - CSV 로드

```bash
python blog_manager.py load --csv data/blogs_list.csv
```

**처리 과정**:
1. CSV 파일 읽기
2. 각 행마다:
   - URL로 기존 블로그 검색
   - 있으면 → UPDATE
   - 없으면 → INSERT
3. 결과 출력 (추가/업데이트 개수)

**CSV 형식**:
```csv
name,url,feed_url,category,priority,active,description,tags
요즘IT,https://yozm.wishket.com,https://yozm.wishket.com/rss,tech,high,true,IT 매거진,tech;development
```

---

### export - CSV 내보내기

```bash
# 기본 내보내기
python blog_manager.py export --csv my_blogs.csv

# 정렬 옵션 지정
python blog_manager.py export --csv my_blogs.csv --sort-by created_at
python blog_manager.py export --csv my_blogs.csv --sort-by name
```

**용도**: 데이터베이스 → CSV 백업

**정렬 옵션**: list 명령과 동일 (category, created_at, name, priority)

---

### list - 블로그 목록

```bash
# 전체 목록 (기본: 카테고리별 정렬)
python blog_manager.py list

# 카테고리 필터
python blog_manager.py list --category ml

# 비활성 포함
python blog_manager.py list --all

# 정렬 옵션
python blog_manager.py list --sort-by created_at  # 등록일 순
python blog_manager.py list --sort-by name         # 이름 순
python blog_manager.py list --sort-by priority     # 우선순위 순
python blog_manager.py list --sort-by category     # 카테고리 순 (기본)

# 조합 사용
python blog_manager.py list --category ml --sort-by created_at --verbose
```

**정렬 옵션**:
- `category` (기본값): 카테고리별 그룹화, 우선순위 내림차순
- `created_at`: 블로그 등록일 기준 내림차순 (최신 등록 먼저)
- `name`: 블로그 이름 알파벳/가나다순 오름차순
- `priority`: 우선순위 내림차순, 같은 우선순위는 이름순

**출력**:
```
📋 블로그 목록 (35개) - 정렬: created_at

[1] 🟢 요즘IT (other)
    등록일: 2026-02-24

[2] 🟢 김단테 블로그 (other)
    등록일: 2026-02-24
...
```

**상세 출력 (--verbose)**:
```
[1] 🟢 요즘 사람들의 IT 매거진, 요즘IT (other)
    URL: https://yozm.wishket.com/magazine/
    Feed: https://yozm.wishket.com/magazine/feed/
    Priority: medium
    등록일: 2026-02-24
...
```

---

### stats - 블로그 통계

```bash
python blog_manager.py stats
```

**출력**:
```
============================================================
📊 블로그 관리 현황
============================================================
전체 블로그: 35개
활성화: 35개 | 비활성화: 0개

카테고리별:
  - other: 25개
  - ml: 4개
  - essay: 4개
  - tech: 1개
  - data: 1개

우선순위별:
  - medium: 35개
============================================================
```

---

### post-stats - 포스트 통계

```bash
python blog_manager.py post-stats
```

**출력**:
```
============================================================
📊 포스트 통계
============================================================
전체 포스트: 341개
오늘 수집: 0개
최근 7일: 341개

블로그별 (상위 10개):
  1. 요즘IT: 10개
  2. 김단테 블로그: 10개
  3. 메르의 블로그: 10개
  ...

카테고리별:
  - other: 250개
  - ml: 40개
  - tech: 30개
  ...
============================================================
```

---

### recent-posts - 최근 포스트

```bash
# 기본 10개
python blog_manager.py recent-posts

# 20개
python blog_manager.py recent-posts --limit 20
```

**출력**:
```
============================================================
📰 최근 포스트 (10개)
============================================================
[1] 시즈오카 이심 추천
    블로그: ☆미라클 여행리포트☆ (other)
    수집: 2024-02-23 21:43:45
    URL: https://blog.naver.com/withjoy79/...

[2] 한올바이오파마 3년만에 돌아온 한올의 시간
    블로그: 벤자민의 투자 이야기 (other)
    수집: 2024-02-23 21:43:45
    URL: https://blog.naver.com/july3003/...
...
```

---

### validate - RSS 피드 검증

```bash
# 간략 출력
python blog_manager.py validate

# 상세 출력
python blog_manager.py validate --verbose
```

**처리**:
- 각 블로그의 RSS 피드에 HTTP 요청
- 응답 코드 확인 (200 = 정상)
- 결과 분류: valid, invalid, no_feed

**출력**:
```
🔍 RSS 피드 검증 중...

✅ 요즘IT
✅ 김단테 블로그
❌ 블로그X (404 Not Found)
⚠️  블로그Y (RSS 없음)

============================================================
📊 검증 결과
============================================================
정상: 33개
오류: 1개
RSS 없음: 1개
============================================================
```

---

## 💻 Python 코드에서 사용

### 기본 사용

```python
from blog_manager import BlogManager

# 초기화
manager = BlogManager()

# 블로그 목록 (기본: 카테고리순)
blogs = manager.list_blogs()
for blog in blogs:
    print(f"{blog['name']}: {blog['url']}")

# 블로그 목록 (등록일순) ⭐ NEW
blogs = manager.list_blogs(sort_by='created_at')
for blog in blogs:
    created = blog['created_at'].split()[0]  # YYYY-MM-DD만 추출
    print(f"[{created}] {blog['name']}")

# 통계
stats = manager.get_stats()
print(f"전체: {stats['total']}개")

# 포스트 통계
post_stats = manager.get_post_stats()
print(f"포스트: {post_stats['total_posts']}개")

# 최근 포스트
recent = manager.get_recent_posts(limit=5)
for post in recent:
    print(f"{post['title']}")
```

---

### CSV 로드

```python
from blog_manager import BlogManager

manager = BlogManager()

# CSV 로드
added, updated = manager.load_from_csv('data/blogs_list.csv')
print(f"추가: {added}, 업데이트: {updated}")

# 결과 확인
manager.print_summary()
```

---

### 필터링 및 정렬

```python
from blog_manager import BlogManager

manager = BlogManager()

# ML 카테고리만
ml_blogs = manager.list_blogs(category='ml')
print(f"ML 블로그: {len(ml_blogs)}개")

# ML 카테고리를 등록일순으로 정렬 ⭐ NEW
ml_blogs = manager.list_blogs(category='ml', sort_by='created_at')
for blog in ml_blogs:
    print(f"{blog['name']} - {blog['created_at']}")

# 모든 블로그 (비활성 포함)
all_blogs = manager.list_blogs(active_only=False)

# 이름순으로 정렬 ⭐ NEW
sorted_blogs = manager.list_blogs(sort_by='name')

# 최근 20개 포스트
recent_posts = manager.get_recent_posts(limit=20)
```

---

## 🔄 워크플로우

### 초기 설정

```bash
# 1. 데이터베이스 생성
python blog_manager.py init

# 2. 블로그 로드
python blog_manager.py load --csv data/blogs_list.csv

# 3. 확인
python blog_manager.py stats
```

---

### 일상 관리

```bash
# 통계 확인
python blog_manager.py post-stats

# 최근 포스트
python blog_manager.py recent-posts --limit 20

# RSS 검증 (월 1회)
python blog_manager.py validate --verbose
```

---

### 백업/복원

```bash
# 백업
python blog_manager.py export --csv backups/blogs_backup.csv

# 복원 (새 DB에)
python blog_manager.py init
python blog_manager.py load --csv backups/blogs_backup.csv
```

---

## 🔍 고급 활용

### SQL 직접 실행

```python
import sqlite3

conn = sqlite3.connect('blogs.db')
cursor = conn.cursor()

# 커스텀 쿼리
cursor.execute("""
    SELECT b.name, COUNT(p.id) as posts
    FROM blogs b
    LEFT JOIN posts p ON b.id = p.blog_id
    WHERE b.category = 'tech'
    GROUP BY b.id
    ORDER BY posts DESC
""")

results = cursor.fetchall()
conn.close()
```

---

### 배치 업데이트

```python
from blog_manager import BlogManager
import sqlite3

manager = BlogManager()
conn = sqlite3.connect('blogs.db')
cursor = conn.cursor()

# 모든 ML 블로그를 high 우선순위로
cursor.execute("""
    UPDATE blogs
    SET priority = 'high'
    WHERE category = 'ml'
""")

conn.commit()
conn.close()

print("✅ ML 블로그 우선순위 업데이트 완료")
```

---

## 🐛 문제 해결

### "No such table: blogs"

**원인**: 데이터베이스 초기화 안됨

**해결**:
```bash
python blog_manager.py init
```

---

### "UNIQUE constraint failed"

**원인**: 중복 URL

**해결**: CSV에서 중복 URL 제거

---

### "database is locked"

**원인**: 다른 프로세스가 DB 사용 중

**해결**:
```bash
# 크롤러 종료
ps aux | grep blog_crawler
kill [PID]

# 또는 PostgreSQL 사용
```

---

## 📚 관련 도구

| 도구 | 용도 |
|------|------|
| `blog_manager.py` | 블로그 DB 관리 |
| `blog_auto_tagger.py` | URL → CSV 자동 생성 |
| `blog_crawler_parallel.py` | 포스트 수집 |
| `app_v2.py` | 웹 대시보드 |

---

## 💡 팁

### 1. CSV 템플릿

```bash
# 템플릿 내보내기
python blog_manager.py export --csv template.csv

# 편집 후 로드
python blog_manager.py load --csv template.csv
```

### 2. 카테고리별 통계

```bash
for cat in ml art tech data essay; do
    echo "=== $cat ==="
    python blog_manager.py list --category $cat | grep "개)"
done
```

### 3. 자동화

```bash
# 매일 통계 저장
python blog_manager.py post-stats > stats/$(date +%Y%m%d).txt
```

---

## ✅ 요약

| 명령어 | 용도 | 주요 옵션 |
|--------|------|----------|
| `init` | DB 초기화 | - |
| `load --csv` | CSV 로드 | `--csv [파일경로]` |
| `export --csv` | CSV 내보내기 | `--csv [파일경로]` `--sort-by [정렬]` |
| `list` | 블로그 목록 | `--category [카테고리]` `--sort-by [정렬]` `--verbose` |
| `stats` | 블로그 통계 | - |
| `post-stats` | 포스트 통계 | - |
| `recent-posts` | 최근 포스트 | `--limit [개수]` |
| `validate` | RSS 검증 | `--verbose` |

**정렬 옵션** (`--sort-by`):
- `category`: 카테고리별 그룹화 (기본값)
- `created_at`: 블로그 등록일순 ⭐ **NEW**
- `name`: 블로그 이름순
- `priority`: 우선순위순

**blog_manager.py로 블로그 데이터를 효율적으로 관리하세요!** 🎉
