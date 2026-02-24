# DBeaver - PostgreSQL 연결 가이드

## 🐘 PostgreSQL 연결 정보

### 기본 설정 (setup_postgres.sh 사용 시)

```
Host:     localhost
Port:     5432
Database: blog_aggregator
Username: postgres
Password: (설정한 비밀번호)
```

### Docker 사용 시

```
Host:     localhost
Port:     5432
Database: blog_aggregator
Username: postgres
Password: mysecretpassword
```

---

## 🔧 연결 단계

### 1. 새 연결 생성
- 메뉴: **Database** → **New Database Connection**
- 또는: `Cmd + N` (macOS) / `Ctrl + N` (Windows)

### 2. PostgreSQL 선택
- **PostgreSQL** 선택
- **Next** 클릭

### 3. 연결 정보 입력

**Main 탭**:
```
┌─────────────────────────────────┐
│ Host:     localhost             │
│ Port:     5432                  │
│ Database: blog_aggregator       │
│ Username: postgres              │
│ Password: [your_password]       │
│                                 │
│ ☑ Show all databases           │
│ ☑ Save password                │
└─────────────────────────────────┘
```

### 4. 드라이버 다운로드 (최초 1회)
- **Download** 클릭 (Driver가 없을 경우)
- PostgreSQL JDBC Driver 자동 다운로드

### 5. 연결 테스트
- **Test Connection** 클릭
- 성공 메시지: "Connected (PostgreSQL xx.x)"

### 6. 완료
- **Finish** 클릭

---

## 📊 데이터베이스 구조

연결 후 왼쪽 패널:

```
blog_aggregator
  └── Schemas
      └── public
          ├── Tables
          │   ├── blogs
          │   ├── posts
          │   ├── bookmarks
          │   └── read_posts
          ├── Views
          │   ├── blog_stats
          │   └── recent_posts
          └── Sequences
              ├── blogs_id_seq
              ├── posts_id_seq
              ├── bookmarks_id_seq
              └── read_posts_id_seq
```

---

## 🔍 샘플 쿼리 (PostgreSQL 전용)

### 1. 최근 포스트 (뷰 사용)

```sql
-- 뷰 사용 (빠른 조회)
SELECT * FROM recent_posts
ORDER BY scraped_at DESC
LIMIT 10;
```

### 2. 블로그 통계 (뷰 사용)

```sql
-- 블로그별 포스트 수와 최신 업데이트
SELECT * FROM blog_stats
ORDER BY post_count DESC;
```

### 3. 전문 검색 (PostgreSQL 고급 기능)

```sql
-- 제목에서 키워드 검색 (대소문자 무시)
SELECT
    p.title,
    b.name as blog_name,
    p.url
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE p.title ILIKE '%투자%'
ORDER BY p.scraped_at DESC
LIMIT 20;
```

### 4. 날짜 범위 조회

```sql
-- 최근 7일간 포스트
SELECT
    DATE(p.scraped_at) as date,
    COUNT(*) as posts_count
FROM posts p
WHERE p.scraped_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(p.scraped_at)
ORDER BY date DESC;
```

### 5. JSON 집계 (PostgreSQL 전용)

```sql
-- 카테고리별 블로그 목록 (JSON)
SELECT
    b.category,
    json_agg(json_build_object(
        'name', b.name,
        'url', b.url,
        'post_count', (SELECT COUNT(*) FROM posts WHERE blog_id = b.id)
    )) as blogs
FROM blogs b
WHERE b.active = TRUE
GROUP BY b.category;
```

---

## 🚀 PostgreSQL 전용 기능

### 1. 쿼리 플랜 분석

```sql
-- 실행 계획 확인
EXPLAIN ANALYZE
SELECT * FROM posts
WHERE blog_id = 1
ORDER BY scraped_at DESC
LIMIT 10;
```

### 2. 인덱스 활용 확인

```sql
-- 인덱스 사용 통계
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### 3. 테이블 크기 확인

```sql
-- 테이블별 디스크 사용량
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 4. 활성 연결 확인

```sql
-- 현재 연결된 세션
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'blog_aggregator';
```

---

## 🎨 DBeaver 고급 설정

### 1. 결과 집합 최적화

**Preferences** → **Database** → **Data Viewer**:
```
☑ Auto-fetch next segment
☑ Use SQL LIMIT/OFFSET
   Result set max size: 1000
```

### 2. SQL 포맷팅

**Preferences** → **SQL Editor** → **Formatting**:
```
Formatter: PostgreSQL
☑ Format SQL on save
☑ Use uppercase keywords
```

### 3. 자동 커밋 설정

**Connection** 우클릭 → **Connection Settings**:
```
☐ Auto-commit (트랜잭션 수동 관리)
```

---

## 📱 유용한 바로 가기 (PostgreSQL)

| 작업 | 단축키 | 설명 |
|------|--------|------|
| 쿼리 실행 | `Cmd/Ctrl + Enter` | 선택된 쿼리 실행 |
| 전체 실행 | `Cmd/Ctrl + Alt + X` | 전체 스크립트 실행 |
| 실행 계획 | `Cmd/Ctrl + E` | EXPLAIN 실행 |
| 트랜잭션 커밋 | `Cmd/Ctrl + Alt + End` | 커밋 |
| 트랜잭션 롤백 | `Cmd/Ctrl + Alt + Home` | 롤백 |

---

## 🔐 보안 설정

### 1. SSH 터널링 (원격 서버)

**SSH 탭**:
```
☑ Use SSH Tunnel
   Host:     your-server.com
   Port:     22
   Username: your-username
   Auth:     Public Key
   Key:      ~/.ssh/id_rsa
```

### 2. SSL 연결

**Driver Properties 탭**:
```
ssl:      true
sslmode:  require
```

---

## 🎯 SQLite vs PostgreSQL 비교

| 기능 | SQLite (DBeaver) | PostgreSQL (DBeaver) |
|------|------------------|----------------------|
| **연결 방식** | 파일 경로 | 네트워크 연결 |
| **동시 접속** | 제한적 | 무제한 ✅ |
| **트랜잭션** | 기본 | 고급 (MVCC) ✅ |
| **뷰** | 단순 | 물리화된 뷰 지원 ✅ |
| **JSON** | 제한적 | 완전 지원 ✅ |
| **전문 검색** | LIKE | ILIKE, Full-text ✅ |
| **쿼리 플랜** | 제한적 | EXPLAIN ANALYZE ✅ |

---

## 🐛 문제 해결

### 연결 실패: "Connection refused"

```bash
# PostgreSQL 실행 확인
brew services list | grep postgresql
# 또는
sudo systemctl status postgresql

# 재시작
brew services restart postgresql@15
```

### 드라이버 다운로드 실패

1. **Help** → **Check for Updates**
2. **Database** → **Driver Manager**
3. PostgreSQL 선택 → **Download/Update**

### 비밀번호 저장 안됨

**Connection Settings** → **Connection**:
```
☑ Save password
Password storage: Master password
```

---

## 📚 PostgreSQL 특화 기능

### 1. 데이터베이스 다이어그램 (ERD)

1. `blog_aggregator` 우클릭
2. **View Diagram** 선택
3. 테이블 관계 자동 시각화

### 2. 데이터 임포트/익스포트

**테이블 우클릭** → **Export Data**:
- CSV, JSON, SQL, XML 지원
- PostgreSQL COPY 명령 사용 (빠름)

### 3. 프로시저/함수 관리

```
Schemas → public → Functions
  └── update_updated_at_column()
```

함수 우클릭 → **View Source**

---

## ✅ 연결 체크리스트

- [ ] PostgreSQL 설치 완료
- [ ] 데이터베이스 생성 (`blog_aggregator`)
- [ ] DBeaver 설치 완료
- [ ] 연결 정보 확인 (.env 파일)
- [ ] 새 연결 생성 (PostgreSQL)
- [ ] Test Connection 성공
- [ ] 테이블 구조 확인
- [ ] 샘플 쿼리 실행

**완료되면 PostgreSQL을 DBeaver에서 관리할 수 있습니다!** 🎉
