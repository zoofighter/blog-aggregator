#!/bin/bash

# 블로그 크롤러 자동 스케줄링 설정 스크립트

echo "🔧 블로그 크롤러 자동 스케줄링 설정"
echo "=================================="
echo ""

# 현재 디렉토리
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="$SCRIPT_DIR/com.blog.crawler.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCHAGENTS_DIR/com.blog.crawler.plist"

# LaunchAgents 디렉토리 생성
mkdir -p "$LAUNCHAGENTS_DIR"

# 기존 스케줄 제거 (있다면)
if [ -f "$TARGET_PLIST" ]; then
    echo "⚠️  기존 스케줄을 제거합니다..."
    launchctl unload "$TARGET_PLIST" 2>/dev/null
    rm "$TARGET_PLIST"
fi

# plist 파일 복사
echo "📋 스케줄 파일을 복사합니다..."
cp "$PLIST_FILE" "$TARGET_PLIST"

# 권한 설정
chmod 644 "$TARGET_PLIST"

# launchctl에 등록
echo "🚀 스케줄을 등록합니다..."
launchctl load "$TARGET_PLIST"

# 상태 확인
if launchctl list | grep -q "com.blog.crawler"; then
    echo ""
    echo "✅ 자동 스케줄링 설정 완료!"
    echo ""
    echo "📅 실행 일정:"
    echo "  - 매일 오전 9시"
    echo "  - 매일 오후 6시"
    echo ""
    echo "📝 로그 파일:"
    echo "  - 일반: $SCRIPT_DIR/crawler.log"
    echo "  - 에러: $SCRIPT_DIR/crawler_error.log"
    echo ""
    echo "🔍 확인 명령어:"
    echo "  launchctl list | grep blog.crawler"
    echo "  tail -f $SCRIPT_DIR/crawler.log"
    echo ""
    echo "🛑 중지 명령어:"
    echo "  launchctl unload $TARGET_PLIST"
    echo ""
else
    echo ""
    echo "❌ 스케줄 등록 실패"
    echo "수동으로 실행해주세요:"
    echo "  launchctl load $TARGET_PLIST"
fi
