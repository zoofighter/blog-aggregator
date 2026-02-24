"""
SQLite → PostgreSQL 마이그레이션 스크립트
기존 SQLite 데이터를 PostgreSQL로 이전
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import argparse
from typing import List, Dict
import os


class DatabaseMigration:
    """데이터베이스 마이그레이션 도구"""

    def __init__(self, sqlite_path: str, pg_config: dict):
        self.sqlite_path = sqlite_path
        self.pg_config = pg_config

    def migrate_all(self, drop_existing: bool = False):
        """전체 마이그레이션 실행"""
        print("\n" + "="*60)
        print("SQLite → PostgreSQL 마이그레이션 시작")
        print("="*60 + "\n")

        # PostgreSQL 연결
        pg_conn = self.connect_postgres()

        try:
            # 1. 스키마 초기화
            if drop_existing:
                print("⚠️  기존 테이블 삭제 중...")
                self.drop_tables(pg_conn)

            print("📋 스키마 생성 중...")
            self.create_schema(pg_conn)

            # 2. 데이터 마이그레이션
            print("\n📦 데이터 마이그레이션 시작...\n")

            # SQLite 연결
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row

            # 순서대로 마이그레이션
            self.migrate_blogs(sqlite_conn, pg_conn)
            self.migrate_posts(sqlite_conn, pg_conn)
            self.migrate_bookmarks(sqlite_conn, pg_conn)
            self.migrate_read_posts(sqlite_conn, pg_conn)

            # 3. 시퀀스 리셋 (PostgreSQL)
            self.reset_sequences(pg_conn)

            # 4. 통계 확인
            self.print_statistics(pg_conn)

            print("\n" + "="*60)
            print("✅ 마이그레이션 완료!")
            print("="*60 + "\n")

        except Exception as e:
            print(f"\n❌ 마이그레이션 실패: {e}")
            raise
        finally:
            pg_conn.close()

    def connect_postgres(self):
        """PostgreSQL 연결"""
        try:
            conn = psycopg2.connect(
                host=self.pg_config['host'],
                port=self.pg_config['port'],
                database=self.pg_config['database'],
                user=self.pg_config['user'],
                password=self.pg_config['password']
            )
            print(f"✅ PostgreSQL 연결: {self.pg_config['database']}@{self.pg_config['host']}")
            return conn
        except psycopg2.OperationalError as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            print("\n데이터베이스가 존재하는지 확인하세요:")
            print(f"  createdb -U {self.pg_config['user']} {self.pg_config['database']}")
            raise

    def drop_tables(self, pg_conn):
        """기존 테이블 삭제"""
        cursor = pg_conn.cursor()
        cursor.execute("""
            DROP TABLE IF EXISTS read_posts CASCADE;
            DROP TABLE IF EXISTS bookmarks CASCADE;
            DROP TABLE IF EXISTS posts CASCADE;
            DROP TABLE IF EXISTS blogs CASCADE;
            DROP VIEW IF EXISTS blog_stats CASCADE;
            DROP VIEW IF EXISTS recent_posts CASCADE;
        """)
        pg_conn.commit()
        cursor.close()

    def create_schema(self, pg_conn):
        """스키마 생성"""
        with open('schema_postgres.sql', 'r', encoding='utf-8') as f:
            schema = f.read()

        cursor = pg_conn.cursor()
        cursor.execute(schema)
        pg_conn.commit()
        cursor.close()
        print("✅ 스키마 생성 완료")

    def migrate_blogs(self, sqlite_conn, pg_conn):
        """블로그 테이블 마이그레이션"""
        print("[1/4] 블로그 마이그레이션...")

        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM blogs")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("  ⏭️  데이터 없음")
            return

        # PostgreSQL INSERT
        pg_cursor = pg_conn.cursor()

        insert_query = """
            INSERT INTO blogs (id, name, url, feed_url, category, priority, active,
                             description, tags, last_crawled, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = []
        for row in rows:
            data.append((
                row['id'],
                row['name'],
                row['url'],
                row['feed_url'],
                row['category'],
                row['priority'],
                row['active'],
                row['description'],
                row['tags'],
                row['last_crawled'],
                row['created_at'],
                row['updated_at'] if 'updated_at' in row.keys() else row['created_at']
            ))

        execute_batch(pg_cursor, insert_query, data)
        pg_conn.commit()
        pg_cursor.close()

        print(f"  ✅ {len(data)}개 블로그 마이그레이션 완료")

    def migrate_posts(self, sqlite_conn, pg_conn):
        """포스트 테이블 마이그레이션"""
        print("[2/4] 포스트 마이그레이션...")

        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM posts")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("  ⏭️  데이터 없음")
            return

        # PostgreSQL INSERT (배치 처리)
        pg_cursor = pg_conn.cursor()

        insert_query = """
            INSERT INTO posts (id, blog_id, title, url, author, published_date,
                             content, summary, image_url, scraped_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 1000개씩 배치 처리
        batch_size = 1000
        total = len(rows)

        for i in range(0, total, batch_size):
            batch = rows[i:i + batch_size]
            data = []

            for row in batch:
                data.append((
                    row['id'],
                    row['blog_id'],
                    row['title'],
                    row['url'],
                    row['author'],
                    row['published_date'],
                    row['content'],
                    row['summary'],
                    row['image_url'],
                    row['scraped_at']
                ))

            execute_batch(pg_cursor, insert_query, data)
            pg_conn.commit()

            processed = min(i + batch_size, total)
            print(f"  📊 진행: {processed}/{total} ({processed/total*100:.1f}%)")

        pg_cursor.close()
        print(f"  ✅ {total}개 포스트 마이그레이션 완료")

    def migrate_bookmarks(self, sqlite_conn, pg_conn):
        """북마크 테이블 마이그레이션"""
        print("[3/4] 북마크 마이그레이션...")

        sqlite_cursor = sqlite_conn.cursor()

        # 테이블 존재 확인
        sqlite_cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='bookmarks'
        """)

        if not sqlite_cursor.fetchone():
            print("  ⏭️  테이블 없음")
            return

        sqlite_cursor.execute("SELECT * FROM bookmarks")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("  ⏭️  데이터 없음")
            return

        # PostgreSQL INSERT
        pg_cursor = pg_conn.cursor()

        insert_query = """
            INSERT INTO bookmarks (id, post_id, created_at)
            VALUES (%s, %s, %s)
        """

        data = [(row['id'], row['post_id'], row['created_at']) for row in rows]

        execute_batch(pg_cursor, insert_query, data)
        pg_conn.commit()
        pg_cursor.close()

        print(f"  ✅ {len(data)}개 북마크 마이그레이션 완료")

    def migrate_read_posts(self, sqlite_conn, pg_conn):
        """읽음 표시 테이블 마이그레이션"""
        print("[4/4] 읽음 표시 마이그레이션...")

        sqlite_cursor = sqlite_conn.cursor()

        # 테이블 존재 확인
        sqlite_cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='read_posts'
        """)

        if not sqlite_cursor.fetchone():
            print("  ⏭️  테이블 없음")
            return

        sqlite_cursor.execute("SELECT * FROM read_posts")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("  ⏭️  데이터 없음")
            return

        # PostgreSQL INSERT
        pg_cursor = pg_conn.cursor()

        insert_query = """
            INSERT INTO read_posts (id, post_id, read_at)
            VALUES (%s, %s, %s)
        """

        data = [(row['id'], row['post_id'], row['read_at']) for row in rows]

        execute_batch(pg_cursor, insert_query, data)
        pg_conn.commit()
        pg_cursor.close()

        print(f"  ✅ {len(data)}개 읽음 표시 마이그레이션 완료")

    def reset_sequences(self, pg_conn):
        """시퀀스 리셋 (PostgreSQL AUTO INCREMENT)"""
        print("\n🔄 시퀀스 리셋 중...")

        cursor = pg_conn.cursor()

        sequences = [
            ('blogs', 'blogs_id_seq'),
            ('posts', 'posts_id_seq'),
            ('bookmarks', 'bookmarks_id_seq'),
            ('read_posts', 'read_posts_id_seq')
        ]

        for table, seq in sequences:
            cursor.execute(f"""
                SELECT setval('{seq}', (SELECT MAX(id) FROM {table}))
            """)

        pg_conn.commit()
        cursor.close()
        print("✅ 시퀀스 리셋 완료")

    def print_statistics(self, pg_conn):
        """마이그레이션 통계 출력"""
        print("\n📊 마이그레이션 통계:")
        print("-" * 60)

        cursor = pg_conn.cursor()

        stats = [
            ('블로그', 'SELECT COUNT(*) FROM blogs'),
            ('포스트', 'SELECT COUNT(*) FROM posts'),
            ('북마크', 'SELECT COUNT(*) FROM bookmarks'),
            ('읽음 표시', 'SELECT COUNT(*) FROM read_posts')
        ]

        for name, query in stats:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  {name:10s}: {count:,}개")

        cursor.close()
        print("-" * 60)


def main():
    """메인 실행"""
    parser = argparse.ArgumentParser(description='SQLite → PostgreSQL 마이그레이션')
    parser.add_argument('--sqlite', default='blogs.db', help='SQLite 파일 경로')
    parser.add_argument('--pg-host', default='localhost', help='PostgreSQL 호스트')
    parser.add_argument('--pg-port', type=int, default=5432, help='PostgreSQL 포트')
    parser.add_argument('--pg-db', default='blog_aggregator', help='PostgreSQL 데이터베이스명')
    parser.add_argument('--pg-user', default='postgres', help='PostgreSQL 사용자')
    parser.add_argument('--pg-password', default='', help='PostgreSQL 비밀번호')
    parser.add_argument('--drop', action='store_true', help='기존 테이블 삭제')

    args = parser.parse_args()

    # PostgreSQL 비밀번호 (환경 변수 우선)
    pg_password = os.getenv('PGPASSWORD', args.pg_password)

    if not pg_password and args.pg_user != os.getenv('USER'):
        import getpass
        pg_password = getpass.getpass(f"PostgreSQL 비밀번호 ({args.pg_user}): ")

    pg_config = {
        'host': args.pg_host,
        'port': args.pg_port,
        'database': args.pg_db,
        'user': args.pg_user,
        'password': pg_password
    }

    # 마이그레이션 실행
    migrator = DatabaseMigration(args.sqlite, pg_config)
    migrator.migrate_all(drop_existing=args.drop)


if __name__ == '__main__':
    main()
