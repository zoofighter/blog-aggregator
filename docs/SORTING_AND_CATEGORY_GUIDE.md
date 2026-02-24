# 블로그 정렬 및 카테고리 관리 가이드 📊

## 📋 개요

블로그 애그리게이터에 **블로그 등록일순 정렬 기능**과 **유연한 정렬 옵션**이 추가되었습니다.

---

## ✨ 새로운 기능

### 1. 다양한 정렬 옵션 (`--sort-by`)

이제 블로그 목록을 다양한 기준으로 정렬할 수 있습니다:

| 정렬 옵션 | 설명 | 정렬 방식 |
|----------|------|-----------|
| `category` | 카테고리별 그룹화 (기본값) | 카테고리 → 우선순위 내림차순 |
| `created_at` | 블로그 등록일순 | 최신 등록 먼저 (내림차순) |
| `last_crawled` | 마지막 크롤링일순 ⭐ **NEW** | 최근 크롤링 먼저 (내림차순) |
| `name` | 블로그 이름순 | 알파벳/가나다순 (오름차순) |
| `priority` | 우선순위순 | 우선순위 내림차순 → 이름순 |

---

## 🚀 사용 방법

### 1. 명령줄(CLI) 사용

#### 기본 목록 조회 (카테고리순)

```bash
python blog_manager.py list
```

#### 등록일순 정렬

```bash
python blog_manager.py list --sort-by created_at
```

**출력 예시**:
```
📋 블로그 목록 (35개) - 정렬: created_at

[1] 🟢 요즘 사람들의 IT 매거진, 요즘IT (other)
    등록일: 2026-02-24 00:02:01
[2] 🟢 피우스의 책도둑 & 매거진 : 네이버 블로그 (other)
    등록일: 2026-02-24 00:02:01
[3] 🟢 메르의 블로그 : 네이버 블로그 (other)
    등록일: 2026-02-24 00:02:01
...
```

#### 크롤링일순 정렬 ⭐ NEW

```bash
python blog_manager.py list --sort-by last_crawled
```

**출력 예시**:
```
📋 블로그 목록 (35개) - 정렬: last_crawled

[1] 🟢 요즘 사람들의 IT 매거진, 요즘IT (other)
    마지막 크롤링: 2026-02-24 00:02:14
[2] 🟢 김단테 : 네이버 블로그 (other)
    마지막 크롤링: 2026-02-24 00:02:14
[3] 🟢 메르의 블로그 : 네이버 블로그 (other)
    마지막 크롤링: 2026-02-24 00:02:14
...
```

**용도**: 최근에 크롤링한 블로그를 먼저 확인하거나, 오랫동안 크롤링되지 않은 블로그를 찾을 때 유용합니다.

#### 이름순 정렬

```bash
python blog_manager.py list --sort-by name
```

**출력 예시**:
```
📋 블로그 목록 (35개) - 정렬: name

[1] 🟢 Aloha life in Hawaii : 네이버 블로그 (ml)
    등록일: 2026-02-24
[2] 🟢 Hodolry의 블로그 : 네이버 블로그 (other)
    등록일: 2026-02-24
[3] 🟢 JH : 네이버 블로그 (other)
    등록일: 2026-02-24
...
```

#### 우선순위순 정렬

```bash
python blog_manager.py list --sort-by priority
```

#### 상세 정보 포함 (--verbose)

```bash
python blog_manager.py list --sort-by created_at --verbose
```

**출력 예시**:
```
[1] 🟢 요즘 사람들의 IT 매거진, 요즘IT (other)
    URL: https://yozm.wishket.com/magazine/
    Feed: https://yozm.wishket.com/magazine/feed/
    Priority: medium
    등록일: 2026-02-24

[2] 🟢 피우스의 책도둑 & 매거진 : 네이버 블로그 (other)
    URL: https://blog.naver.com/jeunkim
    Feed: https://rss.blog.naver.com/jeunkim.xml
    Priority: medium
    등록일: 2026-02-24
...
```

---

### 2. 필터와 정렬 조합

#### ML 카테고리를 등록일순으로

```bash
python blog_manager.py list --category ml --sort-by created_at
```

#### 모든 블로그(비활성 포함)를 이름순으로

```bash
python blog_manager.py list --all --sort-by name
```

#### ML 카테고리 상세 정보 + 등록일순

```bash
python blog_manager.py list --category ml --sort-by created_at --verbose
```

---

### 3. CSV 내보내기 시 정렬

CSV 파일로 내보낼 때도 정렬 옵션을 사용할 수 있습니다:

```bash
# 등록일순으로 정렬하여 내보내기
python blog_manager.py export --csv my_blogs.csv --sort-by created_at

# 이름순으로 정렬하여 내보내기
python blog_manager.py export --csv my_blogs.csv --sort-by name

# 카테고리순으로 정렬하여 내보내기 (기본값)
python blog_manager.py export --csv my_blogs.csv --sort-by category
```

**결과**:
```
✅ CSV 내보내기 완료: my_blogs.csv (35개) - 정렬: created_at
```

---

## 💻 Python 코드에서 사용

### 기본 사용

```python
from blog_manager import BlogManager

manager = BlogManager()

# 기본 정렬 (카테고리순)
blogs = manager.list_blogs()
for blog in blogs:
    print(f"{blog['name']}: {blog['category']}")
```

### 등록일순 정렬

```python
from blog_manager import BlogManager

manager = BlogManager()

# 등록일순으로 블로그 조회
blogs = manager.list_blogs(sort_by='created_at')
for blog in blogs:
    created = blog['created_at'].split()[0]  # YYYY-MM-DD만 추출
    print(f"[등록: {created}] {blog['name']}")
```

**출력 예시**:
```
[등록: 2026-02-24] 요즘 사람들의 IT 매거진, 요즘IT
[등록: 2026-02-24] 피우스의 책도둑 & 매거진 : 네이버 블로그
[등록: 2026-02-24] 메르의 블로그 : 네이버 블로그
...
```

### 크롤링일순 정렬 ⭐ NEW

```python
from blog_manager import BlogManager

manager = BlogManager()

# 크롤링일순으로 블로그 조회
blogs = manager.list_blogs(sort_by='last_crawled')
for blog in blogs:
    crawled = blog.get('last_crawled', 'N/A')
    if crawled and crawled != 'N/A':
        crawled = crawled.split()[0]
    print(f"[크롤링: {crawled}] {blog['name']}")
```

**출력 예시**:
```
[크롤링: 2026-02-24] 요즘 사람들의 IT 매거진, 요즘IT
[크롤링: 2026-02-24] 김단테 : 네이버 블로그
[크롤링: 2026-02-24] 메르의 블로그 : 네이버 블로그
...
```

### 이름순 정렬

```python
# 이름순으로 정렬
sorted_blogs = manager.list_blogs(sort_by='name')
for i, blog in enumerate(sorted_blogs, 1):
    print(f"{i}. {blog['name']}")
```

### 카테고리 + 정렬 조합

```python
# ML 카테고리를 등록일순으로
ml_blogs = manager.list_blogs(category='ml', sort_by='created_at')
print(f"ML 블로그 {len(ml_blogs)}개:")
for blog in ml_blogs:
    print(f"  - {blog['name']} ({blog['created_at']})")
```

### CSV 내보내기 with 정렬

```python
# 등록일순으로 CSV 내보내기
manager.export_to_csv('blogs_by_date.csv', sort_by='created_at')

# 이름순으로 CSV 내보내기
manager.export_to_csv('blogs_by_name.csv', sort_by='name')
```

---

## 📊 현재 카테고리 현황

### 카테고리 분포

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
  - other: 25개  ← 가장 많음 (71%)
  - ml: 4개      (11%)
  - essay: 4개   (11%)
  - tech: 1개    (3%)
  - data: 1개    (3%)

우선순위별:
  - medium: 35개
============================================================
```

### 카테고리별 블로그 목록

```bash
# ML 카테고리만 보기
python blog_manager.py list --category ml

# Essay 카테고리만 보기
python blog_manager.py list --category essay

# Tech 카테고리만 보기
python blog_manager.py list --category tech

# Data 카테고리만 보기
python blog_manager.py list --category data
```

---

## 🔄 카테고리 변경 방법

현재 **"other" 카테고리가 25개(71%)**로 매우 많습니다. 더 구체적으로 분류하고 싶다면 아래 방법을 사용하세요.

### 방법 1: CSV 편집 후 재로드 (권장)

```bash
# 1. 현재 블로그를 CSV로 내보내기
python blog_manager.py export --csv blogs_edit.csv

# 2. CSV 파일을 엑셀이나 텍스트 에디터로 열기
# 3. category 컬럼의 값을 수정
#    예: other → finance, travel, lifestyle 등

# 4. 수정한 CSV를 다시 로드
python blog_manager.py load --csv blogs_edit.csv

# 5. 결과 확인
python blog_manager.py stats
```

**CSV 예시**:
```csv
blog_name,url,feed_url,category,priority,active,description,tags
벤자민의 투자 이야기,https://blog.naver.com/july3003,...,finance,medium,true,...
미라클 여행리포트,https://blog.naver.com/withjoy79,...,travel,medium,true,...
```

### 방법 2: SQL 직접 실행

```bash
# SQLite 데이터베이스 직접 수정
sqlite3 blogs.db

# 투자 관련 블로그를 finance 카테고리로
UPDATE blogs SET category='finance'
WHERE name LIKE '%투자%' OR name LIKE '%주식%';

# 여행 관련 블로그를 travel 카테고리로
UPDATE blogs SET category='travel'
WHERE name LIKE '%여행%';

# 라이프스타일 블로그를 lifestyle 카테고리로
UPDATE blogs SET category='lifestyle'
WHERE description LIKE '%라이프%';

# 결과 확인
SELECT category, COUNT(*) as count
FROM blogs
GROUP BY category
ORDER BY count DESC;

# 종료
.quit
```

### 방법 3: Python 스크립트로 자동 분류

```python
import sqlite3

conn = sqlite3.connect('blogs.db')
cursor = conn.cursor()

# 투자/재테크 블로그 → finance
cursor.execute("""
    UPDATE blogs
    SET category = 'finance'
    WHERE (name LIKE '%투자%'
       OR name LIKE '%주식%'
       OR name LIKE '%경제%'
       OR name LIKE '%재테크%')
    AND category = 'other'
""")

# 여행 블로그 → travel
cursor.execute("""
    UPDATE blogs
    SET category = 'travel'
    WHERE name LIKE '%여행%'
    AND category = 'other'
""")

# IT/기술 블로그 → tech
cursor.execute("""
    UPDATE blogs
    SET category = 'tech'
    WHERE (name LIKE '%IT%'
       OR description LIKE '%기술%'
       OR description LIKE '%개발%')
    AND category = 'other'
""")

conn.commit()

# 결과 확인
cursor.execute("""
    SELECT category, COUNT(*) as count
    FROM blogs
    GROUP BY category
    ORDER BY count DESC
""")

print("\n카테고리 재분류 결과:")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}개")

conn.close()
```

---

## 📝 추천 카테고리 구조

현재 블로그 내용을 보면 다음과 같은 카테고리로 재분류하는 것을 추천합니다:

| 카테고리 | 설명 | 예시 블로그 |
|---------|------|------------|
| `finance` | 투자, 주식, 재테크 | 벤자민의 투자 이야기, 모두의 미국주식 |
| `travel` | 여행, 관광 | 미라클 여행리포트 |
| `lifestyle` | 일상, 라이프스타일 | 골드래빗, 이솔 |
| `tech` | IT, 기술, 개발 | 요즘IT, systrader79 |
| `ml` | AI, 머신러닝 | 제이슨 인사이트, Aloha life |
| `essay` | 에세이, 칼럼 | Yameh, 김명환 |
| `data` | 데이터 분석 | 국내/해외주식 종목분석 |
| `book` | 책, 독서 | 피우스의 책도둑 |

---

## 🎯 실전 예시

### 예시 1: 투자 블로그를 finance 카테고리로 재분류

```bash
# 1. CSV 내보내기
python blog_manager.py export --csv blogs.csv

# 2. 투자 관련 블로그의 category를 finance로 수정
# (엑셀이나 텍스트 에디터 사용)

# 3. 재로드
python blog_manager.py load --csv blogs.csv

# 4. finance 카테고리만 확인
python blog_manager.py list --category finance --sort-by name
```

### 예시 2: 카테고리별 등록일순 정렬

```bash
# ML 블로그를 등록일순으로
python blog_manager.py list --category ml --sort-by created_at

# Finance 블로그를 등록일순으로
python blog_manager.py list --category finance --sort-by created_at

# 모든 블로그를 등록일순으로
python blog_manager.py list --sort-by created_at
```

### 예시 3: 카테고리 통계 자동화

```bash
# 모든 카테고리별 통계 출력
for cat in finance travel lifestyle tech ml essay data book; do
    echo "=== $cat ==="
    python blog_manager.py list --category $cat | head -5
    echo ""
done
```

---

## 💡 활용 팁

### 1. 최근 추가한 블로그 확인

```bash
# 최근 추가한 10개 블로그
python blog_manager.py list --sort-by created_at | head -15
```

### 2. 카테고리별 CSV 백업

```bash
# ML 블로그만 백업
python blog_manager.py list --category ml --sort-by name > ml_blogs.txt

# 모든 카테고리를 개별 CSV로
for cat in ml essay tech data other; do
    python -c "
from blog_manager import BlogManager
import csv

manager = BlogManager()
blogs = manager.list_blogs(category='$cat')

with open('${cat}_blogs.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'url', 'category'])
    writer.writeheader()
    for blog in blogs:
        writer.writerow({'name': blog['name'], 'url': blog['url'], 'category': blog['category']})
    "
done
```

### 3. 등록일 기준으로 정렬된 백업

```bash
# 등록일순으로 정렬하여 CSV 백업 (최신 등록 먼저)
python blog_manager.py export --csv backups/blogs_by_date_$(date +%Y%m%d).csv --sort-by created_at
```

---

## ✅ 요약

### 새로운 정렬 옵션

| 옵션 | 명령 예시 | 설명 |
|------|-----------|------|
| 등록일순 | `python blog_manager.py list --sort-by created_at` | 블로그 추가 날짜 기준 |
| 크롤링일순 ⭐ | `python blog_manager.py list --sort-by last_crawled` | 최근 수집 날짜 기준 |
| 이름순 | `python blog_manager.py list --sort-by name` | 알파벳/가나다순 |
| 우선순위순 | `python blog_manager.py list --sort-by priority` | 우선순위 기준 |
| 카테고리순 | `python blog_manager.py list --sort-by category` | 카테고리별 그룹 (기본) |

### 카테고리 변경

1. **CSV 편집**: `export` → 수정 → `load`
2. **SQL 직접**: `sqlite3 blogs.db`
3. **Python 스크립트**: 자동 재분류

### 조합 사용

```bash
# 카테고리 + 정렬 + 상세정보
python blog_manager.py list --category ml --sort-by created_at --verbose
```

**블로그 정렬과 카테고리 관리로 더 효율적인 블로그 관리를 시작하세요!** 🚀
