# DBeaver - SQLite 연결 가이드

## 📍 연결 정보

**데이터베이스 파일 경로**:
```
/Users/boon/Dropbox/03_code/0223_a/blogs.db
```

## 🔧 연결 단계

### 1. 새 연결 생성
- 메뉴: **Database** → **New Database Connection**
- 또는: `Cmd + N` (macOS) / `Ctrl + N` (Windows)

### 2. SQLite 선택
- **SQLite** 선택
- **Next** 클릭

### 3. 경로 설정
```
Path: /Users/boon/Dropbox/03_code/0223_a/blogs.db
```
- **Browse** 버튼으로 파일 선택
- 또는 경로 직접 입력

### 4. 연결 테스트
- **Test Connection** 클릭
- 성공 메시지 확인: "Connected"

### 5. 완료
- **Finish** 클릭

## 📊 데이터 확인

연결 후 왼쪽 패널에서:

```
blogs.db
  └── Tables
      ├── blogs (35개 블로그)
      ├── posts (341개 포스트)
      ├── bookmarks
      └── read_posts
```

### 쿼리 실행

**SQL 편집기 열기**:
- 테이블 우클릭 → **View Data**
- 또는 `F3`

**샘플 쿼리**:

```sql
-- 전체 블로그 목록
SELECT * FROM blogs ORDER BY name;

-- 최신 포스트 10개
SELECT
    p.title,
    p.url,
    b.name as blog_name,
    p.scraped_at
FROM posts p
JOIN blogs b ON p.blog_id = b.id
ORDER BY p.scraped_at DESC
LIMIT 10;

-- 카테고리별 통계
SELECT
    b.category,
    COUNT(p.id) as post_count
FROM blogs b
LEFT JOIN posts p ON b.id = p.blog_id
GROUP BY b.category
ORDER BY post_count DESC;

-- 블로그별 포스트 수
SELECT
    b.name,
    COUNT(p.id) as posts
FROM blogs b
LEFT JOIN posts p ON b.id = p.blog_id
GROUP BY b.id, b.name
ORDER BY posts DESC;
```

## 🎨 테마 설정 (선택)

**다크 모드**:
- 메뉴: **Window** → **Preferences**
- **General** → **Appearance**
- Theme: **Dark** 선택

## 💡 유용한 기능

### 1. 데이터 편집
- 테이블 우클릭 → **View Data**
- 셀 더블클릭하여 수정
- `Ctrl + S`로 저장

### 2. ERD 다이어그램
- 데이터베이스 우클릭 → **View Diagram**
- 테이블 관계 시각화

### 3. 데이터 내보내기
- 테이블 선택 → 우클릭 → **Export Data**
- CSV, JSON, SQL 등 지원

### 4. SQL 자동 완성
- SQL 편집기에서 `Ctrl + Space`
- 테이블명, 컬럼명 자동 완성

## 📱 바로 가기

| 기능 | macOS | Windows/Linux |
|------|-------|---------------|
| 새 연결 | Cmd+N | Ctrl+N |
| SQL 편집기 | Cmd+\ | Ctrl+\ |
| 쿼리 실행 | Cmd+Enter | Ctrl+Enter |
| 데이터 보기 | F3 | F3 |
| 자동 완성 | Ctrl+Space | Ctrl+Space |

## 🔍 현재 데이터 요약

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 blogs.db 통계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
블로그:   35개
포스트:   341개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

플랫폼별:
  네이버:    23개 (221 포스트)
  브런치:     7개 (70 포스트)
  티스토리:   3개 (30 포스트)
  기타:       2개 (20 포스트)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
