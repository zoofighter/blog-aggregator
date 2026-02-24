#!/bin/bash

# PostgreSQL 설정 자동화 스크립트

echo "🐘 PostgreSQL 설정 시작"
echo "=============================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. PostgreSQL 설치 확인
echo "1️⃣  PostgreSQL 설치 확인..."
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | awk '{print $3}')
    echo -e "${GREEN}✅ PostgreSQL 설치됨: $PG_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL이 설치되지 않았습니다.${NC}"
    echo ""
    echo "설치 방법:"
    echo "  macOS: brew install postgresql@15"
    echo "  Ubuntu: sudo apt install postgresql"
    exit 1
fi

# 2. PostgreSQL 실행 확인
echo ""
echo "2️⃣  PostgreSQL 서비스 확인..."
if pg_isready &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL 실행 중${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL이 실행되지 않았습니다.${NC}"
    echo ""
    echo "시작 방법:"
    echo "  macOS: brew services start postgresql@15"
    echo "  Ubuntu: sudo systemctl start postgresql"
    exit 1
fi

# 3. 데이터베이스 생성
echo ""
echo "3️⃣  데이터베이스 생성..."
DB_NAME=${DB_NAME:-blog_aggregator}
DB_USER=${DB_USER:-postgres}

# 데이터베이스 존재 확인
if psql -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${YELLOW}⚠️  데이터베이스 '$DB_NAME'이 이미 존재합니다.${NC}"
    read -p "삭제하고 다시 만드시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        dropdb -U "$DB_USER" "$DB_NAME" 2>/dev/null
        createdb -U "$DB_USER" "$DB_NAME"
        echo -e "${GREEN}✅ 데이터베이스 재생성 완료${NC}"
    fi
else
    createdb -U "$DB_USER" "$DB_NAME"
    echo -e "${GREEN}✅ 데이터베이스 생성 완료: $DB_NAME${NC}"
fi

# 4. .env 파일 생성
echo ""
echo "4️⃣  환경 변수 설정..."

if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 이미 존재합니다.${NC}"
    read -p "덮어쓰시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "기존 .env 파일 유지"
    else
        rm .env
    fi
fi

if [ ! -f .env ]; then
    read -p "PostgreSQL 비밀번호 (엔터=비밀번호 없음): " DB_PASSWORD

    cat > .env << EOF
# 데이터베이스 설정
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF

    chmod 600 .env
    echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
fi

# 5. Python 패키지 설치
echo ""
echo "5️⃣  Python 패키지 설치..."
if command -v pip &> /dev/null; then
    pip install psycopg2-binary -q
    echo -e "${GREEN}✅ psycopg2-binary 설치 완료${NC}"
else
    echo -e "${RED}❌ pip을 찾을 수 없습니다.${NC}"
    exit 1
fi

# 6. 환경 변수 로드
echo ""
echo "6️⃣  환경 변수 로드..."
export $(cat .env | xargs)
echo -e "${GREEN}✅ 환경 변수 로드 완료${NC}"

# 7. 마이그레이션 실행 여부 확인
echo ""
echo "7️⃣  데이터 마이그레이션..."

if [ -f "blogs.db" ]; then
    # SQLite 데이터 확인
    SQLITE_COUNT=$(sqlite3 blogs.db "SELECT COUNT(*) FROM blogs" 2>/dev/null || echo "0")

    if [ "$SQLITE_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}📦 SQLite에서 ${SQLITE_COUNT}개 블로그 발견${NC}"
        read -p "PostgreSQL로 마이그레이션하시겠습니까? (Y/n): " -n 1 -r
        echo

        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            python migrate_to_postgres.py --drop
        fi
    else
        echo "SQLite 데이터 없음. 스키마만 생성합니다."
        python -c "from db_config import get_db_config; get_db_config().init_database()"
    fi
else
    echo "SQLite 파일 없음. 스키마만 생성합니다."
    python -c "from db_config import get_db_config; get_db_config().init_database()"
fi

# 8. 완료
echo ""
echo "=============================="
echo -e "${GREEN}✅ PostgreSQL 설정 완료!${NC}"
echo "=============================="
echo ""
echo "📝 다음 명령으로 환경 변수 로드:"
echo "   export \$(cat .env | xargs)"
echo ""
echo "🚀 애플리케이션 실행:"
echo "   python app_v2.py"
echo ""
echo "🔍 PostgreSQL 접속:"
echo "   psql -U $DB_USER -d $DB_NAME"
echo ""
