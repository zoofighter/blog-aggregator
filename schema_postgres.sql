-- PostgreSQL 스키마
-- 블로그 애그리게이터 데이터베이스

-- 블로그 테이블
CREATE TABLE IF NOT EXISTS blogs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    feed_url VARCHAR(1000),
    category VARCHAR(50) DEFAULT 'other',
    priority VARCHAR(20) DEFAULT 'medium',
    active BOOLEAN DEFAULT TRUE,
    description TEXT,
    tags TEXT,
    last_crawled TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 포스트 테이블
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    blog_id INTEGER NOT NULL REFERENCES blogs(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url VARCHAR(2000) UNIQUE NOT NULL,
    author VARCHAR(200),
    published_date TIMESTAMP,
    content TEXT,
    summary TEXT,
    image_url VARCHAR(2000),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_blog FOREIGN KEY (blog_id) REFERENCES blogs(id) ON DELETE CASCADE
);

-- 북마크 테이블
CREATE TABLE IF NOT EXISTS bookmarks (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id)
);

-- 읽음 표시 테이블
CREATE TABLE IF NOT EXISTS read_posts (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id)
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_posts_blog_id ON posts(blog_id);
CREATE INDEX IF NOT EXISTS idx_posts_scraped_at ON posts(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_published_date ON posts(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_blogs_active ON blogs(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_blogs_category ON blogs(category);
CREATE INDEX IF NOT EXISTS idx_bookmarks_post_id ON bookmarks(post_id);
CREATE INDEX IF NOT EXISTS idx_read_posts_post_id ON read_posts(post_id);

-- 자동 updated_at 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_blogs_updated_at BEFORE UPDATE ON blogs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 통계 뷰 (빠른 조회)
CREATE OR REPLACE VIEW blog_stats AS
SELECT
    b.id,
    b.name,
    b.category,
    COUNT(p.id) as post_count,
    MAX(p.scraped_at) as last_post_scraped,
    MAX(p.published_date) as last_post_published
FROM blogs b
LEFT JOIN posts p ON b.id = p.blog_id
WHERE b.active = TRUE
GROUP BY b.id, b.name, b.category;

-- 최근 포스트 뷰
CREATE OR REPLACE VIEW recent_posts AS
SELECT
    p.id,
    p.title,
    p.url,
    p.summary,
    p.published_date,
    p.scraped_at,
    b.name as blog_name,
    b.category,
    EXISTS(SELECT 1 FROM bookmarks WHERE post_id = p.id) as is_bookmarked,
    EXISTS(SELECT 1 FROM read_posts WHERE post_id = p.id) as is_read
FROM posts p
JOIN blogs b ON p.blog_id = b.id
WHERE b.active = TRUE
ORDER BY p.scraped_at DESC;
