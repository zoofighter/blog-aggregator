#!/bin/bash

# 데이터베이스 자동 백업 스크립트

echo "💾 데이터베이스 백업 시작..."

# 날짜 포맷
DATE=$(date +%Y%m%d_%H%M%S)

# 프로젝트 경로
PROJECT_DIR="/Users/boon/Dropbox/03_code/0223_a"
cd "$PROJECT_DIR"

# 백업 디렉토리 확인
mkdir -p backups

# 백업 실행
if [ -f "blogs.db" ]; then
    cp blogs.db "backups/blogs_backup_$DATE.db"
    echo "✅ 백업 완료: backups/blogs_backup_$DATE.db"

    # 파일 크기 표시
    du -h "backups/blogs_backup_$DATE.db"
else
    echo "❌ blogs.db 파일을 찾을 수 없습니다."
    exit 1
fi

# 오래된 백업 삭제 (30일 이상)
echo ""
echo "🧹 오래된 백업 정리 중..."
find backups/ -name "blogs_backup_*.db" -mtime +30 -delete
echo "✅ 30일 이상 된 백업 삭제 완료"

# 백업 목록
echo ""
echo "📋 현재 백업 목록:"
ls -lh backups/blogs_backup_*.db | tail -5

echo ""
echo "✅ 백업 작업 완료!"
