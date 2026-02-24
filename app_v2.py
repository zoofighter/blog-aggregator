"""
블로그 애그리게이션 웹 애플리케이션 v2
- 다크모드 지원
- 북마크 기능
- 읽음/안읽음 표시
- 개선된 UI/UX
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI(title="Blog Aggregator v2", description="개인용 블로그 큐레이션 플랫폼")


def get_db_connection():
    """SQLite 연결"""
    conn = sqlite3.connect('blogs.db')
    conn.row_factory = sqlite3.Row
    return conn


# ============= API 엔드포인트 =============

@app.get("/api/posts")
async def get_posts(
    category: Optional[str] = None,
    blog_id: Optional[int] = None,
    search: Optional[str] = None,
    bookmarked: Optional[bool] = None,
    unread: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """포스트 목록 조회 (북마크/읽음 상태 포함)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            p.id, p.title, p.url, p.summary, p.published_date, p.scraped_at, p.image_url,
            b.name as blog_name, b.category, b.url as blog_url,
            CASE WHEN bm.id IS NOT NULL THEN 1 ELSE 0 END as is_bookmarked,
            CASE WHEN rp.id IS NOT NULL THEN 1 ELSE 0 END as is_read
        FROM posts p
        JOIN blogs b ON p.blog_id = b.id
        LEFT JOIN bookmarks bm ON p.id = bm.post_id
        LEFT JOIN read_posts rp ON p.id = rp.post_id
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND b.category = ?"
        params.append(category)

    if blog_id:
        query += " AND p.blog_id = ?"
        params.append(blog_id)

    if search:
        query += " AND (p.title LIKE ? OR p.summary LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    if bookmarked is not None:
        if bookmarked:
            query += " AND bm.id IS NOT NULL"
        else:
            query += " AND bm.id IS NULL"

    if unread is not None:
        if unread:
            query += " AND rp.id IS NULL"
        else:
            query += " AND rp.id IS NOT NULL"

    count_query = f"SELECT COUNT(*) as total FROM ({query})"
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']

    query += " ORDER BY p.scraped_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    posts = []
    for row in rows:
        posts.append({
            'id': row['id'],
            'title': row['title'],
            'url': row['url'],
            'summary': row['summary'],
            'published_date': row['published_date'],
            'scraped_at': row['scraped_at'],
            'image_url': row['image_url'],
            'blog_name': row['blog_name'],
            'category': row['category'],
            'blog_url': row['blog_url'],
            'is_bookmarked': bool(row['is_bookmarked']),
            'is_read': bool(row['is_read'])
        })

    conn.close()

    return {
        'posts': posts,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }


@app.post("/api/bookmarks/{post_id}")
async def add_bookmark(post_id: int):
    """북마크 추가"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO bookmarks (post_id) VALUES (?)", (post_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "북마크 추가됨"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "이미 북마크됨"}


@app.delete("/api/bookmarks/{post_id}")
async def remove_bookmark(post_id: int):
    """북마크 제거"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookmarks WHERE post_id = ?", (post_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected > 0:
        return {"success": True, "message": "북마크 제거됨"}
    else:
        return {"success": False, "message": "북마크 없음"}


@app.post("/api/read/{post_id}")
async def mark_as_read(post_id: int):
    """읽음 표시"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO read_posts (post_id) VALUES (?)", (post_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "읽음 표시"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "이미 읽음"}


@app.delete("/api/read/{post_id}")
async def mark_as_unread(post_id: int):
    """읽지 않음으로 표시"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM read_posts WHERE post_id = ?", (post_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected > 0:
        return {"success": True, "message": "읽지 않음으로 변경"}
    else:
        return {"success": False, "message": "읽음 표시 없음"}


@app.get("/api/stats")
async def get_stats():
    """통계 (북마크/읽음 포함)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM posts")
    total_posts = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as today FROM posts WHERE DATE(scraped_at) = DATE('now')")
    posts_today = cursor.fetchone()['today']

    cursor.execute("SELECT COUNT(*) as count FROM bookmarks")
    total_bookmarks = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM read_posts")
    total_read = cursor.fetchone()['count']

    cursor.execute("""
        SELECT b.category, COUNT(p.id) as count
        FROM blogs b
        LEFT JOIN posts p ON b.id = p.blog_id
        WHERE b.active = TRUE
        GROUP BY b.category
        ORDER BY count DESC
    """)
    by_category = {row['category']: row['count'] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) as total FROM blogs WHERE active = TRUE")
    total_blogs = cursor.fetchone()['total']

    conn.close()

    return {
        'total_posts': total_posts,
        'posts_today': posts_today,
        'total_blogs': total_blogs,
        'total_bookmarks': total_bookmarks,
        'total_read': total_read,
        'unread_count': total_posts - total_read,
        'by_category': by_category
    }


@app.get("/api/categories")
async def get_categories():
    """카테고리 목록"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category, COUNT(*) as count
        FROM blogs
        WHERE active = TRUE
        GROUP BY category
        ORDER BY category
    """)

    categories = [{'name': row['category'], 'count': row['count']} for row in cursor.fetchall()]
    conn.close()
    return categories


@app.get("/api/blogs")
async def get_blogs(sort_by: Optional[str] = 'category'):
    """블로그 목록 (등록일/크롤링일 포함)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 정렬 기준 설정
    if sort_by == 'created_at':
        order_clause = "ORDER BY b.created_at DESC"
    elif sort_by == 'last_crawled':
        order_clause = "ORDER BY b.last_crawled DESC NULLS LAST"
    elif sort_by == 'name':
        order_clause = "ORDER BY b.name ASC"
    elif sort_by == 'priority':
        order_clause = "ORDER BY b.priority DESC, b.name ASC"
    else:  # 'category' (기본값)
        order_clause = "ORDER BY b.category, b.priority DESC"

    cursor.execute(f"""
        SELECT b.id, b.name, b.category, b.url, b.created_at, b.last_crawled, b.priority,
               COUNT(p.id) as post_count
        FROM blogs b
        LEFT JOIN posts p ON b.id = p.blog_id
        WHERE b.active = TRUE
        GROUP BY b.id
        {order_clause}
    """)

    blogs = []
    for row in cursor.fetchall():
        blogs.append({
            'id': row['id'],
            'name': row['name'],
            'category': row['category'],
            'url': row['url'],
            'post_count': row['post_count'],
            'created_at': row['created_at'],
            'last_crawled': row['last_crawled'],
            'priority': row['priority']
        })

    conn.close()
    return blogs


@app.get("/", response_class=HTMLResponse)
async def index():
    """메인 페이지 (다크모드 + 북마크 + 읽음표시)"""
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Aggregator v2</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --bg-primary: #f9fafb;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f3f4f6;
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --accent-color: #3b82f6;
        }

        [data-theme="dark"] {
            --bg-primary: #111827;
            --bg-secondary: #1f2937;
            --bg-tertiary: #374151;
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
            --border-color: #374151;
            --accent-color: #60a5fa;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s, color 0.3s;
        }

        .card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            transition: all 0.2s, background-color 0.3s, border-color 0.3s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }

        .btn {
            transition: all 0.2s;
        }

        .btn:hover {
            transform: scale(1.05);
        }

        .category-badge {
            font-size: 0.75rem;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
        }

        .read-overlay {
            opacity: 0.6;
        }

        .bookmark-icon {
            cursor: pointer;
            transition: all 0.2s;
        }

        .bookmark-icon:hover {
            transform: scale(1.2);
        }

        .bookmarked {
            color: #f59e0b;
            fill: #f59e0b;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="sticky top-0 z-10 shadow-sm" style="background-color: var(--bg-secondary); border-bottom: 1px solid var(--border-color);">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-2xl font-bold">📚 Blog Aggregator v2</h1>
                    <p class="text-sm" style="color: var(--text-secondary);">개인 블로그 큐레이션 플랫폼</p>
                </div>

                <div class="flex items-center gap-4">
                    <!-- 통계 -->
                    <div id="stats" class="flex gap-4 text-sm">
                        <div class="text-center">
                            <div class="text-xl font-bold text-blue-600" id="total-posts">-</div>
                            <div style="color: var(--text-secondary);">포스트</div>
                        </div>
                        <div class="text-center">
                            <div class="text-xl font-bold text-yellow-600" id="total-bookmarks">-</div>
                            <div style="color: var(--text-secondary);">북마크</div>
                        </div>
                        <div class="text-center">
                            <div class="text-xl font-bold text-red-600" id="unread-count">-</div>
                            <div style="color: var(--text-secondary);">안읽음</div>
                        </div>
                    </div>

                    <!-- 다크모드 토글 -->
                    <button onclick="toggleDarkMode()" class="p-2 rounded-lg btn" style="background-color: var(--bg-tertiary);">
                        <span id="theme-icon">🌙</span>
                    </button>
                </div>
            </div>

            <!-- 탭 -->
            <div class="mt-4 flex gap-2 border-b" style="border-color: var(--border-color);">
                <button onclick="switchTab('posts')" id="tab-posts" class="px-4 py-2 font-medium border-b-2 border-blue-600 text-blue-600">
                    📄 포스트
                </button>
                <button onclick="switchTab('blogs')" id="tab-blogs" class="px-4 py-2 font-medium" style="color: var(--text-secondary); border-bottom: 2px solid transparent;">
                    📚 블로그 목록
                </button>
            </div>

            <!-- 포스트 필터 -->
            <div id="post-filters" class="mt-4 flex gap-3 flex-wrap">
                <input
                    type="text"
                    id="search-input"
                    placeholder="포스트 검색..."
                    class="flex-1 px-4 py-2 rounded-lg"
                    style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color);"
                />

                <select id="category-filter" class="px-4 py-2 rounded-lg" style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color);">
                    <option value="">모든 카테고리</option>
                </select>

                <select id="blog-filter" class="px-4 py-2 rounded-lg" style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color);">
                    <option value="">모든 블로그</option>
                </select>

                <div class="flex gap-2">
                    <button onclick="toggleBookmarkFilter()" id="bookmark-filter-btn" class="px-4 py-2 rounded-lg btn" style="background-color: var(--bg-tertiary);">
                        🔖 북마크만
                    </button>
                    <button onclick="toggleUnreadFilter()" id="unread-filter-btn" class="px-4 py-2 rounded-lg btn" style="background-color: var(--bg-tertiary);">
                        📭 안읽음만
                    </button>
                </div>

                <button onclick="loadPosts()" class="px-6 py-2 bg-blue-600 text-white rounded-lg btn hover:bg-blue-700">
                    검색
                </button>
            </div>

            <!-- 블로그 필터 -->
            <div id="blog-filters" class="mt-4 flex gap-3 flex-wrap" style="display: none;">
                <select id="blog-category-filter" class="px-4 py-2 rounded-lg" style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color);">
                    <option value="">모든 카테고리</option>
                </select>

                <select id="blog-sort" class="px-4 py-2 rounded-lg" style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color);">
                    <option value="category">카테고리순</option>
                    <option value="created_at">등록일순 (최신)</option>
                    <option value="last_crawled">크롤링일순 (최근)</option>
                    <option value="name">이름순</option>
                    <option value="priority">우선순위순</option>
                </select>

                <button onclick="loadBlogsList()" class="px-6 py-2 bg-blue-600 text-white rounded-lg btn hover:bg-blue-700">
                    정렬
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div id="loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p class="mt-4" style="color: var(--text-secondary);">로딩 중...</p>
        </div>

        <!-- 포스트 탭 -->
        <div id="posts-tab">
            <div id="posts-container" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3" style="display: none;"></div>
            <div id="pagination" class="mt-8 flex justify-center gap-2" style="display: none;"></div>
            <div id="no-results" class="text-center py-12" style="display: none;">
                <p style="color: var(--text-secondary);" class="text-lg">📭 포스트가 없습니다.</p>
            </div>
        </div>

        <!-- 블로그 목록 탭 -->
        <div id="blogs-tab" style="display: none;">
            <div id="blogs-container" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3"></div>
            <div id="blogs-no-results" class="text-center py-12" style="display: none;">
                <p style="color: var(--text-secondary);" class="text-lg">📭 블로그가 없습니다.</p>
            </div>
        </div>
    </main>

    <script>
        let currentPage = 1;
        let currentTab = 'posts';
        let filters = {
            bookmarked: null,
            unread: null
        };

        const categoryColors = {
            'ml': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
            'art': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
            'tech': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
            'data': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
            'essay': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
            'other': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
        };

        // 탭 전환
        function switchTab(tab) {
            currentTab = tab;

            // 탭 버튼 스타일 변경
            const postsBtn = document.getElementById('tab-posts');
            const blogsBtn = document.getElementById('tab-blogs');

            if (tab === 'posts') {
                postsBtn.className = 'px-4 py-2 font-medium border-b-2 border-blue-600 text-blue-600';
                blogsBtn.className = 'px-4 py-2 font-medium';
                blogsBtn.style.color = 'var(--text-secondary)';
                blogsBtn.style.borderBottom = '2px solid transparent';

                document.getElementById('post-filters').style.display = 'flex';
                document.getElementById('blog-filters').style.display = 'none';
                document.getElementById('posts-tab').style.display = 'block';
                document.getElementById('blogs-tab').style.display = 'none';

                loadPosts();
            } else {
                postsBtn.className = 'px-4 py-2 font-medium';
                postsBtn.style.color = 'var(--text-secondary)';
                postsBtn.style.borderBottom = '2px solid transparent';
                blogsBtn.className = 'px-4 py-2 font-medium border-b-2 border-blue-600 text-blue-600';

                document.getElementById('post-filters').style.display = 'none';
                document.getElementById('blog-filters').style.display = 'flex';
                document.getElementById('posts-tab').style.display = 'none';
                document.getElementById('blogs-tab').style.display = 'block';

                loadBlogsList();
            }
        }

        // 다크모드
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') ||
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            setTheme(savedTheme);
        }

        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            document.getElementById('theme-icon').textContent = theme === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', theme);
        }

        function toggleDarkMode() {
            const current = document.documentElement.getAttribute('data-theme');
            setTheme(current === 'dark' ? 'light' : 'dark');
        }

        // 필터 토글
        function toggleBookmarkFilter() {
            filters.bookmarked = filters.bookmarked === null ? true : null;
            const btn = document.getElementById('bookmark-filter-btn');
            if (filters.bookmarked) {
                btn.style.backgroundColor = '#f59e0b';
                btn.style.color = 'white';
            } else {
                btn.style.backgroundColor = 'var(--bg-tertiary)';
                btn.style.color = 'var(--text-primary)';
            }
            loadPosts(1);
        }

        function toggleUnreadFilter() {
            filters.unread = filters.unread === null ? true : null;
            const btn = document.getElementById('unread-filter-btn');
            if (filters.unread) {
                btn.style.backgroundColor = '#ef4444';
                btn.style.color = 'white';
            } else {
                btn.style.backgroundColor = 'var(--bg-tertiary)';
                btn.style.color = 'var(--text-primary)';
            }
            loadPosts(1);
        }

        // 북마크
        async function toggleBookmark(postId, event) {
            event.stopPropagation();
            event.preventDefault();

            const icon = event.currentTarget;
            const isBookmarked = icon.classList.contains('bookmarked');

            const method = isBookmarked ? 'DELETE' : 'POST';
            const response = await fetch(`/api/bookmarks/${postId}`, { method });
            const data = await response.json();

            if (data.success) {
                icon.classList.toggle('bookmarked');
                icon.textContent = isBookmarked ? '🔖' : '⭐';
                await loadStats();
            }
        }

        // 읽음 표시
        async function markAsRead(postId) {
            await fetch(`/api/read/${postId}`, { method: 'POST' });
            await loadStats();
        }

        // 통계 로드
        async function loadStats() {
            const response = await fetch('/api/stats');
            const data = await response.json();

            document.getElementById('total-posts').textContent = data.total_posts;
            document.getElementById('total-bookmarks').textContent = data.total_bookmarks;
            document.getElementById('unread-count').textContent = data.unread_count;
        }

        // 카테고리 로드
        async function loadCategories() {
            const response = await fetch('/api/categories');
            const categories = await response.json();

            const select = document.getElementById('category-filter');
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.name;
                option.textContent = `${cat.name} (${cat.count})`;
                select.appendChild(option);
            });
        }

        // 블로그 목록 로드 (필터용)
        async function loadBlogs() {
            const response = await fetch('/api/blogs');
            const blogs = await response.json();

            const select = document.getElementById('blog-filter');
            blogs.forEach(blog => {
                const option = document.createElement('option');
                option.value = blog.id;
                option.textContent = `${blog.name} (${blog.post_count})`;
                select.appendChild(option);
            });

            // 블로그 탭 카테고리 필터도 초기화
            const blogCatSelect = document.getElementById('blog-category-filter');
            const categories = [...new Set(blogs.map(b => b.category))];
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                blogCatSelect.appendChild(option);
            });
        }

        // 블로그 목록 로드 (블로그 탭)
        async function loadBlogsList() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('blogs-container').style.display = 'none';

            const sortBy = document.getElementById('blog-sort').value;
            const category = document.getElementById('blog-category-filter').value;

            let url = `/api/blogs?sort_by=${sortBy}`;
            const response = await fetch(url);
            let blogs = await response.json();

            // 카테고리 필터 적용 (클라이언트 측)
            if (category) {
                blogs = blogs.filter(b => b.category === category);
            }

            document.getElementById('loading').style.display = 'none';

            if (blogs.length === 0) {
                document.getElementById('blogs-no-results').style.display = 'block';
                return;
            }

            renderBlogs(blogs);
            document.getElementById('blogs-container').style.display = 'grid';
            document.getElementById('blogs-no-results').style.display = 'none';
        }

        // 블로그 렌더링
        function renderBlogs(blogs) {
            const container = document.getElementById('blogs-container');
            container.innerHTML = '';

            blogs.forEach(blog => {
                const card = createBlogCard(blog);
                container.appendChild(card);
            });
        }

        // 블로그 카드 생성
        function createBlogCard(blog) {
            const card = document.createElement('div');
            card.className = 'card rounded-lg p-5';

            const categoryColor = categoryColors[blog.category] || categoryColors['other'];
            const createdDate = blog.created_at ? formatFullDate(blog.created_at) : 'N/A';
            const lastCrawled = blog.last_crawled ? formatFullDate(blog.last_crawled) : '아직 수집 안함';

            card.innerHTML = `
                <div class="flex items-start justify-between mb-3">
                    <h3 class="text-lg font-semibold flex-1">
                        <a href="${blog.url}" target="_blank" class="hover:text-blue-600">
                            ${blog.name}
                        </a>
                    </h3>
                    <span class="category-badge ${categoryColor}">${blog.category}</span>
                </div>
                <div class="space-y-2 text-sm" style="color: var(--text-secondary);">
                    <div class="flex items-center gap-2">
                        <span>📅 등록일:</span>
                        <span class="font-medium">${createdDate}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span>🔄 마지막 크롤링:</span>
                        <span class="font-medium">${lastCrawled}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span>📝 포스트:</span>
                        <span class="font-medium">${blog.post_count}개</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span>⭐ 우선순위:</span>
                        <span class="font-medium">${blog.priority}</span>
                    </div>
                </div>
                <div class="mt-4">
                    <a href="${blog.url}" target="_blank" class="text-blue-600 hover:underline text-sm">
                        블로그 방문 →
                    </a>
                </div>
            `;

            return card;
        }

        // 포스트 로드
        async function loadPosts(page = 1) {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('posts-container').style.display = 'none';
            document.getElementById('pagination').style.display = 'none';
            document.getElementById('no-results').style.display = 'none';

            currentPage = page;

            const params = new URLSearchParams({
                page: page,
                per_page: 12
            });

            const search = document.getElementById('search-input').value;
            if (search) params.append('search', search);

            const category = document.getElementById('category-filter').value;
            if (category) params.append('category', category);

            const blogId = document.getElementById('blog-filter').value;
            if (blogId) params.append('blog_id', blogId);

            if (filters.bookmarked !== null) params.append('bookmarked', filters.bookmarked);
            if (filters.unread !== null) params.append('unread', filters.unread);

            const response = await fetch(`/api/posts?${params}`);
            const data = await response.json();

            document.getElementById('loading').style.display = 'none';

            if (data.posts.length === 0) {
                document.getElementById('no-results').style.display = 'block';
                return;
            }

            renderPosts(data.posts);
            renderPagination(data.page, data.total_pages);

            document.getElementById('posts-container').style.display = 'grid';
            document.getElementById('pagination').style.display = 'flex';
        }

        // 포스트 렌더링
        function renderPosts(posts) {
            const container = document.getElementById('posts-container');
            container.innerHTML = '';

            posts.forEach(post => {
                const card = createPostCard(post);
                container.appendChild(card);
            });
        }

        // 포스트 카드 생성
        function createPostCard(post) {
            const card = document.createElement('div');
            card.className = 'card rounded-lg overflow-hidden' + (post.is_read ? ' read-overlay' : '');

            const categoryColor = categoryColors[post.category] || categoryColors['other'];
            const summary = post.summary || '요약이 없습니다.';
            const summaryPreview = summary.length > 150 ? summary.substring(0, 150) + '...' : summary;

            const bookmarkIcon = post.is_bookmarked ? '⭐' : '🔖';
            const bookmarkClass = post.is_bookmarked ? 'bookmarked' : '';

            card.innerHTML = `
                ${post.image_url ? `
                    <img src="${post.image_url}" alt="${post.title}" class="w-full h-48 object-cover" onerror="this.style.display='none'">
                ` : ''}
                <div class="p-5">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                            <span class="category-badge ${categoryColor}">${post.category}</span>
                            <span class="text-xs" style="color: var(--text-secondary);">${formatDate(post.scraped_at)}</span>
                        </div>
                        <span class="bookmark-icon ${bookmarkClass}" onclick="toggleBookmark(${post.id}, event)">${bookmarkIcon}</span>
                    </div>
                    <h3 class="text-lg font-semibold mb-2 line-clamp-2">
                        <a href="${post.url}" target="_blank" onclick="markAsRead(${post.id})" class="hover:text-blue-600">
                            ${post.title}
                        </a>
                    </h3>
                    <p class="text-sm mb-3 line-clamp-3" style="color: var(--text-secondary);">${summaryPreview}</p>
                    <div class="flex items-center justify-between text-xs" style="color: var(--text-secondary);">
                        <span>📝 ${post.blog_name}</span>
                        <a href="${post.url}" target="_blank" onclick="markAsRead(${post.id})" class="text-blue-600 hover:underline">
                            원문 보기 →
                        </a>
                    </div>
                </div>
            `;

            return card;
        }

        // 페이지네이션
        function renderPagination(currentPage, totalPages) {
            const container = document.getElementById('pagination');
            container.innerHTML = '';

            if (currentPage > 1) {
                const prevBtn = createPageButton('← 이전', currentPage - 1);
                container.appendChild(prevBtn);
            }

            const startPage = Math.max(1, currentPage - 2);
            const endPage = Math.min(totalPages, currentPage + 2);

            for (let i = startPage; i <= endPage; i++) {
                const btn = createPageButton(i, i, i === currentPage);
                container.appendChild(btn);
            }

            if (currentPage < totalPages) {
                const nextBtn = createPageButton('다음 →', currentPage + 1);
                container.appendChild(nextBtn);
            }
        }

        function createPageButton(text, page, isActive = false) {
            const btn = document.createElement('button');
            btn.textContent = text;
            btn.onclick = () => loadPosts(page);
            btn.className = isActive
                ? 'px-4 py-2 bg-blue-600 text-white rounded-lg'
                : 'px-4 py-2 rounded-lg btn';
            if (!isActive) {
                btn.style.backgroundColor = 'var(--bg-secondary)';
                btn.style.border = '1px solid var(--border-color)';
            }
            return btn;
        }

        function formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (minutes < 60) return `${minutes}분 전`;
            if (hours < 24) return `${hours}시간 전`;
            if (days < 7) return `${days}일 전`;

            return date.toLocaleDateString('ko-KR');
        }

        function formatFullDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');

            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        }

        // Enter 키로 검색
        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') loadPosts();
        });

        // 블로그 정렬 변경 시 자동 로드
        document.getElementById('blog-sort').addEventListener('change', loadBlogsList);
        document.getElementById('blog-category-filter').addEventListener('change', loadBlogsList);

        // 초기화
        async function init() {
            initTheme();
            await loadStats();
            await loadCategories();
            await loadBlogs();
            await loadPosts();
        }

        init();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌐 블로그 애그리게이터 v2 웹 서버 시작")
    print("="*60)
    print("새 기능:")
    print("  🌙 다크모드 (자동 감지 + 수동 토글)")
    print("  🔖 북마크 기능")
    print("  ✅ 읽음/안읽음 표시")
    print("  🎨 개선된 UI/UX")
    print("="*60)
    print(f"URL: http://localhost:8000")
    print(f"API 문서: http://localhost:8000/docs")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
