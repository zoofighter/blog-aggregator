"""
이메일 다이제스트 시스템
매일 또는 매주 새 포스트 요약을 이메일로 전송
"""

import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict
import argparse


class EmailDigest:
    """이메일 다이제스트 생성 및 전송"""

    def __init__(self, db_path: str = "blogs.db"):
        self.db_path = db_path

    def get_recent_posts(self, days: int = 1) -> List[Dict]:
        """최근 N일간 수집된 포스트"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.title, p.url, p.summary, p.scraped_at,
                   b.name as blog_name, b.category
            FROM posts p
            JOIN blogs b ON p.blog_id = b.id
            WHERE DATE(p.scraped_at) >= DATE('now', ?)
            ORDER BY p.scraped_at DESC
        """, (f'-{days} days',))

        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row['id'],
                'title': row['title'],
                'url': row['url'],
                'summary': row['summary'] or '요약 없음',
                'scraped_at': row['scraped_at'],
                'blog_name': row['blog_name'],
                'category': row['category']
            })

        conn.close()
        return posts

    def get_category_stats(self, days: int = 1) -> Dict[str, int]:
        """카테고리별 포스트 수"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.category, COUNT(p.id) as count
            FROM posts p
            JOIN blogs b ON p.blog_id = b.id
            WHERE DATE(p.scraped_at) >= DATE('now', ?)
            GROUP BY b.category
            ORDER BY count DESC
        """, (f'-{days} days',))

        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]

        conn.close()
        return stats

    def generate_html_digest(self, posts: List[Dict], period: str = "오늘") -> str:
        """HTML 이메일 다이제스트 생성"""
        category_stats = self.get_category_stats(1 if period == "오늘" else 7)

        # 카테고리별 색상
        category_colors = {
            'ml': '#9333ea',
            'art': '#ec4899',
            'tech': '#3b82f6',
            'data': '#10b981',
            'essay': '#f59e0b',
            'other': '#6b7280'
        }

        # 카테고리별 이모지
        category_icons = {
            'ml': '🤖',
            'art': '🎨',
            'tech': '💻',
            'data': '📊',
            'essay': '✍️',
            'other': '📄'
        }

        # 통계 HTML
        stats_html = ""
        for cat, count in category_stats.items():
            color = category_colors.get(cat, '#6b7280')
            icon = category_icons.get(cat, '📄')
            stats_html += f'''
                <div style="display: inline-block; padding: 8px 16px; margin: 4px;
                           background-color: {color}20; color: {color};
                           border-radius: 20px; font-size: 14px;">
                    {icon} {cat}: {count}개
                </div>
            '''

        # 포스트 HTML
        posts_html = ""
        for post in posts:
            cat_color = category_colors.get(post['category'], '#6b7280')
            cat_icon = category_icons.get(post['category'], '📄')

            summary = post['summary'][:200] + ('...' if len(post['summary']) > 200 else '')

            posts_html += f'''
                <div style="border: 1px solid #e5e7eb; border-radius: 8px;
                           padding: 20px; margin-bottom: 16px; background-color: #ffffff;">
                    <div style="margin-bottom: 12px;">
                        <span style="background-color: {cat_color}20; color: {cat_color};
                                   padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                            {cat_icon} {post['category']}
                        </span>
                        <span style="color: #9ca3af; font-size: 12px; margin-left: 8px;">
                            {post['blog_name']}
                        </span>
                    </div>
                    <h3 style="margin: 0 0 8px 0; font-size: 18px;">
                        <a href="{post['url']}" style="color: #111827; text-decoration: none;">
                            {post['title']}
                        </a>
                    </h3>
                    <p style="color: #6b7280; font-size: 14px; margin: 0 0 12px 0; line-height: 1.5;">
                        {summary}
                    </p>
                    <a href="{post['url']}" style="color: #3b82f6; text-decoration: none; font-size: 14px;">
                        원문 보기 →
                    </a>
                </div>
            '''

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                     background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;
                       border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">

                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           padding: 30px; border-radius: 12px 12px 0 0; color: white;">
                    <h1 style="margin: 0 0 8px 0; font-size: 28px;">📚 Blog Digest</h1>
                    <p style="margin: 0; font-size: 16px; opacity: 0.9;">{period}의 새로운 포스트</p>
                </div>

                <!-- Stats -->
                <div style="padding: 24px; border-bottom: 1px solid #e5e7eb;">
                    <h2 style="margin: 0 0 16px 0; font-size: 20px; color: #111827;">📊 요약</h2>
                    <div style="margin-bottom: 12px;">
                        <span style="font-size: 32px; font-weight: bold; color: #3b82f6;">{len(posts)}</span>
                        <span style="color: #6b7280; margin-left: 8px;">개의 새 포스트</span>
                    </div>
                    <div style="margin-top: 16px;">
                        {stats_html}
                    </div>
                </div>

                <!-- Posts -->
                <div style="padding: 24px;">
                    <h2 style="margin: 0 0 20px 0; font-size: 20px; color: #111827;">📰 포스트</h2>
                    {posts_html if posts else '<p style="color: #9ca3af; text-align: center; padding: 40px 0;">새 포스트가 없습니다.</p>'}
                </div>

                <!-- Footer -->
                <div style="padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;
                           color: #9ca3af; font-size: 12px;">
                    <p style="margin: 0;">Blog Aggregator - 개인 블로그 큐레이션 플랫폼</p>
                    <p style="margin: 8px 0 0 0;">
                        <a href="http://localhost:8000" style="color: #3b82f6; text-decoration: none;">
                            대시보드 보기 →
                        </a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''

        return html

    def send_email(self, to_email: str, subject: str, html_content: str,
                   smtp_server: str = "smtp.gmail.com",
                   smtp_port: int = 587,
                   from_email: str = None,
                   password: str = None):
        """이메일 전송"""

        if not from_email or not password:
            print("⚠️  이메일 전송을 위해서는 SMTP 설정이 필요합니다.")
            print("    --from-email과 --password 옵션을 사용하세요.")
            return False

        try:
            # 이메일 구성
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = from_email
            message['To'] = to_email

            # HTML 파트 추가
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)

            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(message)

            print(f"✅ 이메일 전송 완료: {to_email}")
            return True

        except Exception as e:
            print(f"❌ 이메일 전송 실패: {str(e)}")
            return False

    def save_digest_html(self, html_content: str, filename: str = None):
        """다이제스트를 HTML 파일로 저장 (미리보기용)"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"digest_{timestamp}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 다이제스트 저장: {filename}")
        return filename


def main():
    """메인 실행"""
    parser = argparse.ArgumentParser(description='이메일 다이제스트 생성/전송')
    parser.add_argument('--days', type=int, default=1, help='최근 N일 (기본: 1)')
    parser.add_argument('--preview', action='store_true', help='HTML 파일로 미리보기')
    parser.add_argument('--send', action='store_true', help='이메일 전송')
    parser.add_argument('--to-email', help='받는 사람 이메일')
    parser.add_argument('--from-email', help='보내는 사람 이메일 (Gmail)')
    parser.add_argument('--password', help='Gmail 앱 비밀번호')

    args = parser.parse_args()

    digest = EmailDigest()

    # 포스트 가져오기
    posts = digest.get_recent_posts(days=args.days)

    period = "오늘" if args.days == 1 else f"최근 {args.days}일"
    print(f"\n📊 {period}: {len(posts)}개 포스트")

    # HTML 생성
    html_content = digest.generate_html_digest(posts, period=period)

    # 미리보기
    if args.preview or not args.send:
        filename = digest.save_digest_html(html_content)
        print(f"\n브라우저에서 확인: open {filename}")

    # 이메일 전송
    if args.send:
        if not args.to_email:
            print("❌ --to-email 옵션이 필요합니다.")
            return

        subject = f"📚 Blog Digest - {period}의 새 포스트 {len(posts)}개"

        digest.send_email(
            to_email=args.to_email,
            subject=subject,
            html_content=html_content,
            from_email=args.from_email,
            password=args.password
        )


if __name__ == '__main__':
    main()
