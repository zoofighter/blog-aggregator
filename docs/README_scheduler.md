# 자동 스케줄링 설정 가이드 ⏰

블로그 크롤러를 정기적으로 자동 실행하는 방법입니다.

## 🚀 빠른 시작

### 1. 자동 설정 스크립트 실행

```bash
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

**완료!** 이제 매일 오전 9시와 오후 6시에 자동으로 크롤링됩니다.

## ⚙️ 설정 상세

### 실행 일정

기본 설정 (수정 가능):
- **매일 오전 9시**: 아침에 새 글 수집
- **매일 오후 6시**: 저녁에 추가 수집

### 크롤링 설정

- **포스트 수 제한**: 블로그당 10개 (`--limit 10`)
- **작업 디렉토리**: `/Users/boon/Dropbox/03_code/0223_a`
- **로그 파일**:
  - `crawler.log` - 실행 로그
  - `crawler_error.log` - 에러 로그

## 📋 수동 설정 (상세)

자동 스크립트가 작동하지 않으면 수동으로 설정하세요:

### 1. plist 파일 복사

```bash
cp com.blog.crawler.plist ~/Library/LaunchAgents/
```

### 2. 권한 설정

```bash
chmod 644 ~/Library/LaunchAgents/com.blog.crawler.plist
```

### 3. launchd 등록

```bash
launchctl load ~/Library/LaunchAgents/com.blog.crawler.plist
```

### 4. 확인

```bash
launchctl list | grep blog.crawler
```

출력 예시:
```
-    0    com.blog.crawler
```

## 🛠 일정 수정하기

`com.blog.crawler.plist` 파일을 편집하세요:

### 하루에 한 번만 (오전 9시)

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### 3시간마다

```xml
<key>StartInterval</key>
<integer>10800</integer>  <!-- 3시간 = 10800초 -->
```

### 매주 월요일 오전 9시만

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>
    <integer>1</integer>  <!-- 0=일요일, 1=월요일 -->
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

**수정 후 재등록:**
```bash
launchctl unload ~/Library/LaunchAgents/com.blog.crawler.plist
launchctl load ~/Library/LaunchAgents/com.blog.crawler.plist
```

## 📊 로그 확인

### 실시간 로그 보기

```bash
# 일반 로그
tail -f crawler.log

# 에러 로그
tail -f crawler_error.log
```

### 최근 실행 확인

```bash
# 최근 50줄
tail -50 crawler.log

# 오늘 실행 내역
grep "$(date +%Y-%m-%d)" crawler.log
```

### 로그 예시

```
🚀 11개 블로그 크롤링 시작...

[1/11] Yameh의 브런치
   ✅ 3개 수집

[2/11] 모두의 미국주식
   ✅ 5개 수집

...

✅ 완료! 총 45개 신규 포스트 수집
```

## 🔧 문제 해결

### 스케줄이 실행되지 않아요

**1. 등록 상태 확인**
```bash
launchctl list | grep blog.crawler
```

없으면 다시 등록:
```bash
launchctl load ~/Library/LaunchAgents/com.blog.crawler.plist
```

**2. 에러 로그 확인**
```bash
cat crawler_error.log
```

**3. 수동 테스트**
```bash
# 스케줄러 통하지 않고 직접 실행
python blog_crawler.py --limit 10 --verbose
```

### 로그 파일이 너무 커져요

**로그 순환 (자동 정리)**

```bash
# 30일 이상 된 로그 삭제
find . -name "crawler*.log" -mtime +30 -delete

# 또는 cron으로 자동화
# crontab -e
# 0 0 1 * * find /path/to/logs -name "*.log" -mtime +30 -delete
```

### Permission denied 에러

```bash
# Python 경로 확인
which python3

# plist 파일에서 ProgramArguments 수정
# /usr/bin/python3 → 실제 python3 경로
```

## 🛑 스케줄 중지/제거

### 일시 중지

```bash
launchctl unload ~/Library/LaunchAgents/com.blog.crawler.plist
```

### 다시 시작

```bash
launchctl load ~/Library/LaunchAgents/com.blog.crawler.plist
```

### 완전 제거

```bash
launchctl unload ~/Library/LaunchAgents/com.blog.crawler.plist
rm ~/Library/LaunchAgents/com.blog.crawler.plist
```

## 📱 알림 추가 (선택)

크롤링 완료 시 알림을 받고 싶다면:

**1. 알림 스크립트 생성** (`crawler_with_notification.sh`):

```bash
#!/bin/bash
cd /Users/boon/Dropbox/03_code/0223_a

# 크롤링 실행
python blog_crawler.py --limit 10 > /tmp/crawler_output.txt 2>&1

# 결과 확인
if grep -q "완료!" /tmp/crawler_output.txt; then
    # 성공 알림
    osascript -e 'display notification "새 포스트를 수집했습니다!" with title "블로그 크롤러"'
else
    # 실패 알림
    osascript -e 'display notification "크롤링에 실패했습니다" with title "블로그 크롤러" sound name "Basso"'
fi
```

**2. plist 수정**:
```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>/Users/boon/Dropbox/03_code/0223_a/crawler_with_notification.sh</string>
</array>
```

## 🎯 추천 설정

### 개인용 (100개 블로그)

**일정**: 하루 2회 (오전 9시, 오후 6시)
**포스트 제한**: 10개
**예상 신규 포스트**: 20-50개/일

### 헤비 유저 (200+ 블로그)

**일정**: 3시간마다
**포스트 제한**: 5개
**성능**: Rate limiting으로 약 10분 소요

## 📈 모니터링

### 통계 대시보드

매일 실행되는 통계 요약:

```bash
# crontab에 추가
# 매일 오후 7시에 통계 이메일
0 19 * * * cd /path && python blog_manager.py post-stats > /tmp/stats.txt && mail -s "Blog Stats" your@email.com < /tmp/stats.txt
```

### Webhook 알림

Slack, Discord 등으로 알림 전송:

```python
# blog_crawler.py 끝에 추가
import requests

webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
requests.post(webhook_url, json={
    "text": f"✅ 크롤링 완료: {total_new_posts}개 신규 포스트"
})
```

## 🔐 보안

### 크론 권한 확인

macOS Catalina 이상에서는 "전체 디스크 접근 권한" 필요:

1. **시스템 설정** → **개인정보 보호 및 보안**
2. **전체 디스크 접근 권한**
3. **+** 버튼 → `/usr/sbin/cron` 추가

## 💡 팁

### 배터리 절약

노트북 사용 시 배터리일 때는 스킵:

```xml
<key>RunAtLoad</key>
<false/>

<!-- 추가 -->
<key>StartOnMyMac</key>
<true/>
```

### 네트워크 확인

네트워크 연결되었을 때만 실행:

```bash
# 스크립트에 추가
if ! ping -c 1 google.com &> /dev/null; then
    echo "네트워크 없음, 종료"
    exit 1
fi
```

---

**설정 완료 후** 다음날 아침 확인해보세요!

```bash
# 어제/오늘 수집된 포스트 확인
python blog_manager.py recent-posts --limit 20
```
