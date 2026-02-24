# 웹 대시보드 사용 가이드 🌐

## 🚀 빠른 시작

### 1단계: 서버 실행

```bash
python app_v2.py
```

### 2단계: 브라우저 접속

```
http://localhost:8000
```

**끝!** 웹 대시보드가 표시됩니다 ✨

---

## 🏗️ 웹 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────┐
│  브라우저 (Chrome, Safari 등)           │
│  http://localhost:8000                  │
│                                         │
│  ┌───────────────────────────────┐     │
│  │  HTML                          │     │
│  │  - 포스트 카드                 │     │
│  │  - 필터 버튼                   │     │
│  │  - 다크모드 토글               │     │
│  └───────────┬───────────────────┘     │
│              │                          │
│  ┌───────────▼───────────────────┐     │
│  │  JavaScript                    │     │
│  │  - API 호출                    │     │
│  │  - 동적 업데이트               │     │
│  │  - 이벤트 처리                 │     │
│  └───────────┬───────────────────┘     │
│              │ fetch('/api/posts')     │
└──────────────┼─────────────────────────┘
               │ HTTP Request
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI 서버 (app_v2.py)              │
│  Port: 8000                             │
│                                         │
│  ┌───────────────────────────────┐     │
│  │  라우터 (Routes)              │     │
│  │  GET  /                       │     │
│  │  GET  /api/posts              │     │
│  │  POST /api/bookmarks/{id}     │     │
│  │  GET  /api/stats              │     │
│  └───────────┬───────────────────┘     │
│              │                          │
│  ┌───────────▼───────────────────┐     │
│  │  비즈니스 로직                │     │
│  │  - 페이징 처리                │     │
│  │  - 필터링                     │     │
│  │  - 데이터 변환                │     │
│  └───────────┬───────────────────┘     │
│              │ SQL Query               │
└──────────────┼─────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  SQLite Database (blogs.db)            │
│                                         │
│  ┌─────────────┐  ┌─────────────┐     │
│  │   blogs     │  │   posts     │     │
│  │  (35개)     │  │  (341개)    │     │
│  └─────────────┘  └─────────────┘     │
│                                         │
│  ┌─────────────┐  ┌─────────────┐     │
│  │  bookmarks  │  │ read_posts  │     │
│  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────┘
```

---

## 🔄 요청 흐름 (예시: 포스트 목록 조회)

### 1. 사용자가 페이지 접속

```
브라우저 → GET http://localhost:8000/
```

### 2. 서버가 HTML 반환

```python
@app.get("/")
async def root():
    return HTMLResponse(html_content)
```

브라우저가 HTML 받아서 표시

### 3. JavaScript가 API 호출

```javascript
// 페이지 로드 시 자동 실행
async function loadPosts() {
    // API 요청
    const response = await fetch('/api/posts?page=1&per_page=12');
    const data = await response.json();
    displayPosts(data.posts);
}
```

### 4. 서버가 데이터 조회

```python
@app.get("/api/posts")
async def get_posts(page: int = 1, per_page: int = 12):
    # DB 연결
    conn = sqlite3.connect('blogs.db')
    cursor = conn.cursor()

    # SQL 실행
    cursor.execute("""
        SELECT p.*, b.name as blog_name, b.category
        FROM posts p
        JOIN blogs b ON p.blog_id = b.id
        ORDER BY p.scraped_at DESC
        LIMIT ? OFFSET ?
    """, (per_page, (page-1)*per_page))

    posts = cursor.fetchall()

    # JSON 반환
    return {"posts": posts, "total": total}
```

### 5. JavaScript가 화면 업데이트

```javascript
function displayPosts(posts) {
    const container = document.getElementById('posts-container');

    posts.forEach(post => {
        // 카드 HTML 생성
        const card = `
            <div class="post-card">
                <h3>${post.title}</h3>
                <p>${post.summary}</p>
                <a href="${post.url}">원문 보기</a>
            </div>
        `;
        container.innerHTML += card;
    });
}
```

---

## 📡 API 엔드포인트 상세

### 1. **메인 페이지**

```
GET /
```

**응답**: HTML 페이지

---

### 2. **포스트 목록**

```
GET /api/posts
```

**파라미터**:
- `page` (int): 페이지 번호 (기본: 1)
- `per_page` (int): 페이지당 개수 (기본: 12)
- `category` (str): 카테고리 필터
- `blog_id` (int): 블로그 필터
- `bookmarked` (bool): 북마크만 보기
- `unread` (bool): 안읽은 것만 보기

**예시**:
```bash
# 1페이지 (12개)
curl http://localhost:8000/api/posts?page=1

# ML 카테고리만
curl http://localhost:8000/api/posts?category=ml

# 북마크만
curl http://localhost:8000/api/posts?bookmarked=true

# 조합
curl http://localhost:8000/api/posts?category=tech&page=2&per_page=20
```

**응답**:
```json
{
  "posts": [
    {
      "id": 1,
      "title": "포스트 제목",
      "url": "https://...",
      "summary": "요약...",
      "blog_name": "블로그명",
      "category": "tech",
      "is_bookmarked": false,
      "is_read": false
    }
  ],
  "total": 341,
  "page": 1,
  "per_page": 12
}
```

---

### 3. **통계**

```
GET /api/stats
```

**응답**:
```json
{
  "total_posts": 341,
  "total_blogs": 35,
  "bookmarked_count": 5,
  "unread_count": 300
}
```

---

### 4. **카테고리 목록**

```
GET /api/categories
```

**응답**:
```json
{
  "categories": [
    {"name": "ml", "count": 50},
    {"name": "tech", "count": 100},
    {"name": "data", "count": 80}
  ]
}
```

---

### 5. **블로그 목록**

```
GET /api/blogs
```

**응답**:
```json
{
  "blogs": [
    {
      "id": 1,
      "name": "요즘IT",
      "category": "tech",
      "post_count": 10
    }
  ]
}
```

---

### 6. **북마크 추가**

```
POST /api/bookmarks/{post_id}
```

**예시**:
```bash
curl -X POST http://localhost:8000/api/bookmarks/123
```

**응답**:
```json
{
  "success": true,
  "message": "북마크 추가됨"
}
```

---

### 7. **북마크 제거**

```
DELETE /api/bookmarks/{post_id}
```

---

### 8. **읽음 표시**

```
POST /api/read/{post_id}
```

---

### 9. **읽음 취소**

```
DELETE /api/read/{post_id}
```

---

## 🎨 프론트엔드 기능

### 1. **다크모드**

- 자동 감지: 시스템 설정 따라감
- 수동 토글: 우측 상단 버튼

**구현**:
```javascript
// 다크모드 감지
const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
if (darkModeMediaQuery.matches) {
    document.body.classList.add('dark');
}

// 토글 버튼
function toggleDarkMode() {
    document.body.classList.toggle('dark');
    localStorage.setItem('darkMode', isDark);
}
```

---

### 2. **북마크**

- 클릭으로 추가/제거
- 실시간 업데이트
- "북마크만 보기" 필터

**구현**:
```javascript
async function toggleBookmark(postId) {
    const isBookmarked = await checkBookmark(postId);

    if (isBookmarked) {
        await fetch(`/api/bookmarks/${postId}`, { method: 'DELETE' });
    } else {
        await fetch(`/api/bookmarks/${postId}`, { method: 'POST' });
    }

    // UI 업데이트
    updateBookmarkIcon(postId);
}
```

---

### 3. **필터링**

- 카테고리 필터
- 블로그 필터
- 북마크/읽음 필터
- 조합 가능

**구현**:
```javascript
function applyFilters() {
    const params = new URLSearchParams();

    if (selectedCategory) params.append('category', selectedCategory);
    if (selectedBlog) params.append('blog_id', selectedBlog);
    if (bookmarkedOnly) params.append('bookmarked', 'true');
    if (unreadOnly) params.append('unread', 'true');

    loadPosts(params.toString());
}
```

---

### 4. **페이징**

- 12개씩 표시
- 이전/다음 버튼
- 무한 스크롤 (선택)

**구현**:
```javascript
function loadNextPage() {
    currentPage++;
    loadPosts(`page=${currentPage}`);
}
```

---

## 🛠️ 개발자 도구 활용

### Chrome DevTools

1. **Network 탭**: API 요청 확인
   - F12 → Network
   - 페이지 새로고침
   - `/api/posts` 클릭하여 응답 확인

2. **Console 탭**: JavaScript 오류 확인
   - F12 → Console
   - 에러 메시지 확인

3. **Application 탭**: LocalStorage 확인
   - F12 → Application → Local Storage
   - darkMode 설정 확인

---

## 🔧 커스터마이징

### 포트 변경

```python
# app_v2.py 마지막 줄
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # 8000 → 8080
```

### 페이지당 포스트 수 변경

```python
@app.get("/api/posts")
async def get_posts(per_page: int = 20):  # 12 → 20
    # ...
```

### CSS 커스터마이징

`app_v2.py` 내부 HTML에서 `<style>` 태그 수정:

```css
:root {
    --primary-color: #3b82f6;  /* 파랑 → 다른 색상 */
    --card-bg: #ffffff;
}
```

---

## 🐛 문제 해결

### 포트 이미 사용 중

```
Error: [Errno 48] Address already in use
```

**해결**:
```bash
# 프로세스 확인
lsof -i :8000

# 종료
kill -9 [PID]
```

### 데이터베이스 잠금

```
sqlite3.OperationalError: database is locked
```

**해결**:
- 크롤러 실행 중이면 종료
- 또는 PostgreSQL 사용

### API 응답 없음

**확인 사항**:
1. 서버 실행 중?
2. 데이터베이스 존재?
3. 브라우저 Console에 에러?

---

## 📱 모바일 접속

같은 네트워크에 있으면 모바일에서도 접속 가능:

1. 서버 실행:
   ```bash
   python app_v2.py
   ```

2. IP 확인:
   ```bash
   ifconfig | grep "inet "
   # 192.168.1.100
   ```

3. 모바일 브라우저:
   ```
   http://192.168.1.100:8000
   ```

---

## 🚀 프로덕션 배포

### 1. 환경 변수 설정

```bash
export DB_TYPE=postgresql
export DB_HOST=your-db-host
```

### 2. Gunicorn 사용 (권장)

```bash
# 설치
pip install gunicorn

# 실행
gunicorn app_v2:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 3. Nginx 프록시 (선택)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 💡 팁

### 1. API 문서 활용

```
http://localhost:8000/docs
```

- 모든 API 테스트 가능
- 자동 생성된 문서
- Swagger UI

### 2. 백그라운드 실행

```bash
# 백그라운드에서 실행
nohup python app_v2.py > web.log 2>&1 &

# 로그 확인
tail -f web.log
```

### 3. 자동 재시작

```bash
# nodemon 사용 (파일 변경 시 재시작)
npm install -g nodemon
nodemon --exec python app_v2.py
```

---

## ✅ 요약

| 항목 | 내용 |
|------|------|
| **실행 방법** | `python app_v2.py` |
| **접속 URL** | http://localhost:8000 |
| **API 문서** | http://localhost:8000/docs |
| **기술 스택** | FastAPI + SQLite + Vanilla JS |
| **포트** | 8000 (변경 가능) |

**웹 대시보드로 블로그 포스트를 편리하게 관리하세요!** 🎉
