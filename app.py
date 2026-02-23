"""
블로그 애그리게이션 웹 애플리케이션
FastAPI 백엔드 + HTML 프론트엔드
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Dict
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI(title="Blog Aggregator", description="개인용 블로그 큐레이션 플랫폼")


# 데이터베이스 헬퍼
def get_db_connection():
    """SQLite 연결"""
    conn = sqlite3.connect('blogs.db')
    conn.row_factory = sqlite3.Row
    return conn


# API 엔드포인트

@app.get("/api/posts")
async def get_posts(
    category: Optional[str] = None,
    blog_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """포스트 목록 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 기본 쿼리
    query = """
        SELECT
            p.id, p.title, p.url, p.summary, p.published_date, p.scraped_at, p.image_url,
            b.name as blog_name, b.category, b.url as blog_url
        FROM posts p
        JOIN blogs b ON p.blog_id = b.id
        WHERE 1=1
    """
    params = []

    # 필터 조건 추가
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

    # 전체 개수 조회
    count_query = f"SELECT COUNT(*) as total FROM ({query})"
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']

    # 페이지네이션
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
            'blog_url': row['blog_url']
        })

    conn.close()

    return {
        'posts': posts,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }


@app.get("/api/stats")
async def get_stats():
    """통계 정보"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 전체 포스트 수
    cursor.execute("SELECT COUNT(*) as total FROM posts")
    total_posts = cursor.fetchone()['total']

    # 오늘 수집된 포스트
    cursor.execute("SELECT COUNT(*) as today FROM posts WHERE DATE(scraped_at) = DATE('now')")
    posts_today = cursor.fetchone()['today']

    # 카테고리별 포스트 수
    cursor.execute("""
        SELECT b.category, COUNT(p.id) as count
        FROM blogs b
        LEFT JOIN posts p ON b.id = p.blog_id
        WHERE b.active = TRUE
        GROUP BY b.category
        ORDER BY count DESC
    """)
    by_category = {row['category']: row['count'] for row in cursor.fetchall()}

    # 블로그 수
    cursor.execute("SELECT COUNT(*) as total FROM blogs WHERE active = TRUE")
    total_blogs = cursor.fetchone()['total']

    conn.close()

    return {
        'total_posts': total_posts,
        'posts_today': posts_today,
        'total_blogs': total_blogs,
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
async def get_blogs():
    """블로그 목록"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.id, b.name, b.category, b.url,
               COUNT(p.id) as post_count
        FROM blogs b
        LEFT JOIN posts p ON b.id = p.blog_id
        WHERE b.active = TRUE
        GROUP BY b.id
        ORDER BY b.category, b.name
    """)

    blogs = []
    for row in cursor.fetchall():
        blogs.append({
            'id': row['id'],
            'name': row['name'],
            'category': row['category'],
            'url': row['url'],
            'post_count': row['post_count']
        })

    conn.close()
    return blogs


@app.get("/", response_class=HTMLResponse)
async def index():
    """메인 페이지"""
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Aggregator - 개인 블로그 큐레이션</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .post-card {
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .post-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .category-badge {
            font-size: 0.75rem;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">📚 Blog Aggregator</h1>
                    <p class="text-sm text-gray-600">개인 블로그 큐레이션 플랫폼</p>
                </div>
                <div id="stats" class="flex gap-6 text-sm">
                    <div class="text-center">
                        <div class="text-2xl font-bold text-blue-600" id="total-posts">-</div>
                        <div class="text-gray-600">포스트</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-green-600" id="total-blogs">-</div>
                        <div class="text-gray-600">블로그</div>
                    </div>
                </div>
            </div>

            <!-- 검색 및 필터 -->
            <div class="mt-4 flex gap-3">
                <input
                    type="text"
                    id="search-input"
                    placeholder="포스트 검색..."
                    class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <select
                    id="category-filter"
                    class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">모든 카테고리</option>
                </select>
                <select
                    id="blog-filter"
                    class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">모든 블로그</option>
                </select>
                <button
                    onclick="loadPosts()"
                    class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    검색
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div id="loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">로딩 중...</p>
        </div>

        <div id="posts-container" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3" style="display: none;">
            <!-- 포스트 카드가 여기에 동적으로 추가됩니다 -->
        </div>

        <div id="pagination" class="mt-8 flex justify-center gap-2" style="display: none;">
            <!-- 페이지네이션 버튼 -->
        </div>

        <div id="no-results" class="text-center py-12" style="display: none;">
            <p class="text-gray-600 text-lg">📭 포스트가 없습니다.</p>
            <p class="text-gray-500 mt-2">크롤러를 실행해서 포스트를 수집하세요.</p>
            <code class="block mt-4 bg-gray-100 p-3 rounded">python blog_crawler.py</code>
        </div>
    </main>

    <script>
        let currentPage = 1;
        let currentFilters = {};

        // 카테고리 색상 매핑
        const categoryColors = {
            'ml': 'bg-purple-100 text-purple-800',
            'art': 'bg-pink-100 text-pink-800',
            'tech': 'bg-blue-100 text-blue-800',
            'data': 'bg-green-100 text-green-800',
            'essay': 'bg-yellow-100 text-yellow-800',
            'other': 'bg-gray-100 text-gray-800'
        };

        // 초기 로드
        async function init() {
            await loadStats();
            await loadCategories();
            await loadBlogs();
            await loadPosts();
        }

        // 통계 로드
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();

                document.getElementById('total-posts').textContent = data.total_posts;
                document.getElementById('total-blogs').textContent = data.total_blogs;
            } catch (error) {
                console.error('통계 로드 실패:', error);
            }
        }

        // 카테고리 로드
        async function loadCategories() {
            try {
                const response = await fetch('/api/categories');
                const categories = await response.json();

                const select = document.getElementById('category-filter');
                categories.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.name;
                    option.textContent = `${cat.name} (${cat.count})`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('카테고리 로드 실패:', error);
            }
        }

        // 블로그 목록 로드
        async function loadBlogs() {
            try {
                const response = await fetch('/api/blogs');
                const blogs = await response.json();

                const select = document.getElementById('blog-filter');
                blogs.forEach(blog => {
                    const option = document.createElement('option');
                    option.value = blog.id;
                    option.textContent = `${blog.name} (${blog.post_count})`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('블로그 로드 실패:', error);
            }
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

            try {
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
            } catch (error) {
                console.error('포스트 로드 실패:', error);
                document.getElementById('loading').style.display = 'none';
            }
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
            card.className = 'post-card bg-white rounded-lg shadow-sm overflow-hidden';

            const categoryColor = categoryColors[post.category] || categoryColors['other'];
            const summary = post.summary || '요약이 없습니다.';
            const summaryPreview = summary.length > 150 ? summary.substring(0, 150) + '...' : summary;

            card.innerHTML = `
                ${post.image_url ? `
                    <img src="${post.image_url}" alt="${post.title}" class="w-full h-48 object-cover" onerror="this.style.display='none'">
                ` : ''}
                <div class="p-5">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="category-badge ${categoryColor}">${post.category}</span>
                        <span class="text-xs text-gray-500">${formatDate(post.scraped_at)}</span>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                        <a href="${post.url}" target="_blank" class="hover:text-blue-600">
                            ${post.title}
                        </a>
                    </h3>
                    <p class="text-sm text-gray-600 mb-3 line-clamp-3">${summaryPreview}</p>
                    <div class="flex items-center justify-between text-xs text-gray-500">
                        <span>📝 ${post.blog_name}</span>
                        <a href="${post.url}" target="_blank" class="text-blue-600 hover:underline">
                            원문 보기 →
                        </a>
                    </div>
                </div>
            `;

            return card;
        }

        // 페이지네이션 렌더링
        function renderPagination(currentPage, totalPages) {
            const container = document.getElementById('pagination');
            container.innerHTML = '';

            // 이전 버튼
            if (currentPage > 1) {
                const prevBtn = createPageButton('← 이전', currentPage - 1);
                container.appendChild(prevBtn);
            }

            // 페이지 번호
            const startPage = Math.max(1, currentPage - 2);
            const endPage = Math.min(totalPages, currentPage + 2);

            for (let i = startPage; i <= endPage; i++) {
                const btn = createPageButton(i, i, i === currentPage);
                container.appendChild(btn);
            }

            // 다음 버튼
            if (currentPage < totalPages) {
                const nextBtn = createPageButton('다음 →', currentPage + 1);
                container.appendChild(nextBtn);
            }
        }

        // 페이지 버튼 생성
        function createPageButton(text, page, isActive = false) {
            const btn = document.createElement('button');
            btn.textContent = text;
            btn.onclick = () => loadPosts(page);
            btn.className = isActive
                ? 'px-4 py-2 bg-blue-600 text-white rounded-lg'
                : 'px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 border border-gray-300';
            return btn;
        }

        // 날짜 포맷
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

        // Enter 키로 검색
        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') loadPosts();
        });

        // 페이지 로드 시 실행
        init();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌐 블로그 애그리게이터 웹 서버 시작")
    print("="*60)
    print(f"URL: http://localhost:8000")
    print(f"API 문서: http://localhost:8000/docs")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
