#!/bin/bash

# 블로그 애그리게이터 빠른 설정 스크립트

echo "🚀 블로그 애그리게이터 빠른 설정"
echo "===================================="
echo ""

# 색상
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. PostgreSQL 설치 여부 확인
echo "1️⃣  PostgreSQL 확인..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL 설치됨${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL이 설치되지 않았습니다.${NC}"
    echo ""
    read -p "지금 설치하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v brew &> /dev/null; then
            brew install postgresql@15
            brew services start postgresql@15
            echo -e "${GREEN}✅ PostgreSQL 설치 완료${NC}"
        else
            echo "Homebrew가 필요합니다: https://brew.sh"
            exit 1
        fi
    else
        echo "SQLite를 사용합니다."
        USE_SQLITE=true
    fi
fi

# 2. 데이터베이스 선택
echo ""
echo "2️⃣  데이터베이스 선택..."
if [ "$USE_SQLITE" = true ]; then
    DB_TYPE="sqlite"
else
    echo "어떤 데이터베이스를 사용하시겠습니까?"
    echo "  1) SQLite (간단, 파일 기반)"
    echo "  2) PostgreSQL (강력, 프로덕션)"
    read -p "선택 (1 또는 2): " -n 1 -r
    echo
    if [[ $REPLY == "2" ]]; then
        DB_TYPE="postgresql"
    else
        DB_TYPE="sqlite"
    fi
fi

# 3. 설정 파일 생성
echo ""
echo "3️⃣  설정 파일 생성..."

if [ "$DB_TYPE" = "sqlite" ]; then
    cat > .env << 'EOF'
DB_TYPE=sqlite
DB_PATH=blogs.db
EOF
    echo -e "${GREEN}✅ SQLite 설정 완료${NC}"

else
    # PostgreSQL 설정
    echo ""
    echo "PostgreSQL 설정:"
    read -p "비밀번호를 설정하시겠습니까? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -s -p "PostgreSQL 비밀번호 입력: " DB_PASSWORD
        echo
        read -s -p "비밀번호 확인: " DB_PASSWORD_CONFIRM
        echo

        if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
            echo -e "${YELLOW}⚠️  비밀번호가 일치하지 않습니다.${NC}"
            exit 1
        fi

        # 비밀번호 설정
        psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
    else
        DB_PASSWORD=""
    fi

    # .env 파일 생성
    cat > .env << EOF
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=blog_aggregator
DB_USER=postgres
DB_PASSWORD=$DB_PASSWORD
EOF

    chmod 600 .env
    echo -e "${GREEN}✅ PostgreSQL 설정 완료${NC}"

    # 데이터베이스 생성
    echo ""
    echo "4️⃣  데이터베이스 생성..."
    if createdb -U postgres blog_aggregator 2>/dev/null; then
        echo -e "${GREEN}✅ blog_aggregator 데이터베이스 생성${NC}"
    else
        echo -e "${YELLOW}⚠️  데이터베이스가 이미 존재하거나 권한 문제${NC}"
    fi
fi

# 4. Python 패키지 설치
echo ""
echo "5️⃣  Python 패키지 설치..."
if [ "$DB_TYPE" = "postgresql" ]; then
    pip install psycopg2-binary -q
    echo -e "${GREEN}✅ PostgreSQL 드라이버 설치${NC}"
fi

pip install -r requirements.txt -q
echo -e "${GREEN}✅ 필수 패키지 설치 완료${NC}"

# 5. 데이터베이스 초기화
echo ""
echo "6️⃣  데이터베이스 초기화..."
if [ "$DB_TYPE" = "postgresql" ]; then
    export $(cat .env | xargs)
    python -c "from db_config import get_db_config; get_db_config().init_database()" 2>/dev/null
    echo -e "${GREEN}✅ PostgreSQL 스키마 생성${NC}"
else
    python -c "from blog_manager import BlogManager; BlogManager().init_database()" 2>/dev/null
    echo -e "${GREEN}✅ SQLite 데이터베이스 생성${NC}"
fi

# 완료
echo ""
echo "===================================="
echo -e "${GREEN}✅ 설정 완료!${NC}"
echo "===================================="
echo ""
echo "📊 현재 설정:"
cat .env
echo ""
echo "🚀 다음 단계:"
echo "   1. 블로그 추가:"
echo "      python blog_auto_tagger.py --file blogs_list.csv"
echo "      python blog_manager.py load --csv analyzed_blogs.csv"
echo ""
echo "   2. 포스트 수집:"
echo "      python blog_crawler_parallel.py --limit 10"
echo ""
echo "   3. 웹 대시보드:"
echo "      python app_v2.py"
echo ""
