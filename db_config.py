"""
데이터베이스 설정 및 연결 관리
SQLite와 PostgreSQL 모두 지원
"""

import os
from typing import Optional, Any
from contextlib import contextmanager


class DatabaseConfig:
    """데이터베이스 설정 관리"""

    def __init__(self):
        # 환경 변수에서 DB 타입 결정 (기본값: sqlite)
        self.db_type = os.getenv('DB_TYPE', 'sqlite').lower()

        if self.db_type == 'postgresql':
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'database': os.getenv('DB_NAME', 'blog_aggregator'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
            }
        else:
            self.db_config = {
                'database': os.getenv('DB_PATH', 'blogs.db')
            }

    def get_connection(self):
        """데이터베이스 연결 반환"""
        if self.db_type == 'postgresql':
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            return conn
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_config['database'])
            conn.row_factory = sqlite3.Row
            return conn

    @contextmanager
    def get_cursor(self):
        """커서 컨텍스트 매니저"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def execute_query(self, query: str, params: tuple = None) -> list:
        """쿼리 실행 (SELECT)"""
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if self.db_type == 'postgresql':
                # PostgreSQL: fetchall() 직접 사용
                return cursor.fetchall()
            else:
                # SQLite: Row 객체를 딕셔너리로 변환
                return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = None) -> int:
        """쿼리 실행 (INSERT, UPDATE, DELETE)"""
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount

    def get_placeholder(self) -> str:
        """파라미터 플레이스홀더 반환"""
        if self.db_type == 'postgresql':
            return '%s'
        else:
            return '?'

    def get_returning_clause(self, column: str = 'id') -> str:
        """RETURNING 절 반환 (INSERT 후 ID 가져오기)"""
        if self.db_type == 'postgresql':
            return f' RETURNING {column}'
        else:
            return ''

    def init_database(self):
        """데이터베이스 초기화"""
        if self.db_type == 'postgresql':
            self._init_postgresql()
        else:
            self._init_sqlite()

    def _init_postgresql(self):
        """PostgreSQL 초기화"""
        import psycopg2

        # 스키마 파일 읽기
        with open('schema_postgres.sql', 'r', encoding='utf-8') as f:
            schema = f.read()

        # 실행
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(schema)
            conn.commit()
            print(f"✅ PostgreSQL 데이터베이스 초기화 완료: {self.db_config['database']}")
        except Exception as e:
            conn.rollback()
            print(f"❌ PostgreSQL 초기화 실패: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def _init_sqlite(self):
        """SQLite 초기화 (기존 코드)"""
        from blog_manager import BlogManager
        manager = BlogManager()
        manager.init_database()


class QueryBuilder:
    """SQL 쿼리 빌더 (PostgreSQL/SQLite 호환)"""

    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.placeholder = db_config.get_placeholder()

    def insert(self, table: str, columns: list, values: list) -> str:
        """INSERT 쿼리 생성"""
        placeholders = ', '.join([self.placeholder] * len(columns))
        columns_str = ', '.join(columns)

        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        # PostgreSQL: RETURNING id 추가
        if self.db_config.db_type == 'postgresql':
            query += " RETURNING id"

        return query

    def select(self, table: str, columns: list = None, where: dict = None,
               order_by: str = None, limit: int = None, offset: int = None) -> tuple:
        """SELECT 쿼리 생성"""
        cols = ', '.join(columns) if columns else '*'
        query = f"SELECT {cols} FROM {table}"
        params = []

        # WHERE 절
        if where:
            conditions = []
            for col, val in where.items():
                conditions.append(f"{col} = {self.placeholder}")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)

        # ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"

        # LIMIT & OFFSET
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return query, tuple(params)

    def update(self, table: str, set_values: dict, where: dict) -> tuple:
        """UPDATE 쿼리 생성"""
        set_clause = ', '.join([f"{col} = {self.placeholder}" for col in set_values.keys()])
        query = f"UPDATE {table} SET {set_clause}"
        params = list(set_values.values())

        # WHERE 절
        if where:
            conditions = []
            for col, val in where.items():
                conditions.append(f"{col} = {self.placeholder}")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)

        return query, tuple(params)

    def delete(self, table: str, where: dict) -> tuple:
        """DELETE 쿼리 생성"""
        query = f"DELETE FROM {table}"
        params = []

        # WHERE 절
        if where:
            conditions = []
            for col, val in where.items():
                conditions.append(f"{col} = {self.placeholder}")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)

        return query, tuple(params)


# 전역 인스턴스
_db_config = None

def get_db_config() -> DatabaseConfig:
    """데이터베이스 설정 싱글톤"""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config


if __name__ == '__main__':
    # 테스트
    print("데이터베이스 설정 테스트")
    print("=" * 60)

    config = get_db_config()
    print(f"DB 타입: {config.db_type}")
    print(f"설정: {config.db_config}")
    print(f"플레이스홀더: {config.get_placeholder()}")

    # 쿼리 빌더 테스트
    builder = QueryBuilder(config)

    # INSERT 예시
    insert_query = builder.insert('blogs', ['name', 'url'], ['Test Blog', 'https://test.com'])
    print(f"\nINSERT: {insert_query}")

    # SELECT 예시
    select_query, params = builder.select('posts',
                                          columns=['id', 'title'],
                                          where={'blog_id': 1},
                                          order_by='scraped_at DESC',
                                          limit=10)
    print(f"SELECT: {select_query}")
    print(f"Params: {params}")
