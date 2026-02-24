# 블로그 크롤러 사용 가이드 📡

RSS 피드에서 블로그 포스트를 자동으로 수집하는 크롤러입니다.

## ✅ 완료된 작업

- ✅ 11개 블로그 등록 완료
- ✅ RSS 피드 자동 수집 시스템 구축
- ✅ 자동 요약 생성 (200자)
- ✅ 50개 포스트 수집 성공

## 🚀 빠른 시작

### 1. 모든 블로그 크롤링

```bash
python blog_crawler.py
```

**결과**:
- 11개 블로그에서 각각 최대 10개 포스트 수집
- 중복 제거 자동 처리
- 요약 자동 생성

### 2. 포스트 수 제한

```bash
# 블로그당 최대 5개만 수집
python blog_crawler.py --limit 5

# 블로그당 최대 20개 수집
python blog_crawler.py --limit 20
```

### 3. 상세 출력 모드

```bash
python blog_crawler.py --verbose
```

각 포스트가 저장되는 과정을 실시간으로 확인할 수 있습니다.

### 4. 특정 블로그만 크롤링

```bash
# 블로그 ID 확인
python blog_manager.py list

# ID 1번 블로그만 크롤링
python blog_crawler.py --blog-id 1 --verbose
```

## 📊 수집 결과 확인

### 통계 보기

```bash
python blog_manager.py post-stats
```

출력 예시:
```
============================================================
📝 포스트 수집 현황
============================================================
전체 포스트: 50개
오늘 수집: 50개

블로그별 포스트 수:
  - Yameh의 브런치: 5개
  - 모두의 미국주식: 5개
  - ...
============================================================
```

### 최근 포스트 조회

```bash
# 최근 10개
python blog_manager.py recent-posts

# 최근 20개
python blog_manager.py recent-posts --limit 20
```

출력 예시:
```
📰 최근 포스트 5개

[essay] AI 에이전트들의 팀워크 - 다중 에이전트 시스템의 탄생
   블로그: Yameh의 브런치
   요약: AI 에이전트가 서로 협력하여 복잡한 작업을 수행하는 다중 에이전트 시스템에 대해...
   URL: https://brunch.co.kr/...
```

### DB 직접 조회

```bash
# 전체 포스트 수
sqlite3 blogs.db "SELECT COUNT(*) FROM posts;"

# 최근 5개 제목
sqlite3 blogs.db "SELECT title FROM posts ORDER BY scraped_at DESC LIMIT 5;"

# 카테고리별 포스트 수
sqlite3 blogs.db "SELECT b.category, COUNT(p.id) FROM blogs b JOIN posts p ON b.id = p.blog_id GROUP BY b.category;"
```

## 🎯 주요 기능

### 1. 자동 RSS 파싱
- feedparser 라이브러리 사용
- 네이버 블로그, 브런치 등 다양한 플랫폼 지원
- 오류 발생 시에도 다른 블로그 계속 처리

### 2. 포스트 데이터 추출
수집되는 정보:
- ✅ 제목
- ✅ URL
- ✅ 작성자
- ✅ 발행일
- ✅ 본문 내용
- ✅ 이미지 URL (대표 이미지)
- ✅ 자동 생성 요약 (200자)

### 3. 중복 제거
- URL 기준 중복 체크
- 이미 수집된 포스트는 자동으로 건너뜀
- 재실행해도 중복 저장 없음

### 4. 자동 요약
```python
# HTML 태그 제거 → 공백 정리 → 200자로 자르기
"AI 에이전트가 서로 협력하여 복잡한 작업을 수행하는 다중 에이전트 시스템에 대해 알아봅니다. 최근 AI 기술의 발전으로 단일 에이전트가 아닌 여러 에이전트가 협업하는 시스템이 주목받고 있습니다..."
```

### 5. Rate Limiting
- 블로그 간 2초 대기
- 서버 부하 방지
- 안정적인 크롤링

## 📁 데이터베이스 구조

### posts 테이블
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    blog_id INTEGER,           -- 블로그 ID (외래키)
    title TEXT,                -- 포스트 제목
    url TEXT UNIQUE,           -- 포스트 URL (중복 방지)
    author TEXT,               -- 작성자
    published_date TIMESTAMP,  -- 발행일
    content TEXT,              -- 원본 내용
    summary TEXT,              -- 자동 생성 요약
    image_url TEXT,            -- 대표 이미지
    scraped_at TIMESTAMP       -- 수집 시각
)
```

## 🔄 정기 크롤링 설정

### cron (macOS/Linux)

```bash
# crontab 편집
crontab -e

# 매일 오전 9시 크롤링
0 9 * * * cd /path/to/project && python blog_crawler.py --limit 10

# 3시간마다 크롤링
0 */3 * * * cd /path/to/project && python blog_crawler.py --limit 5
```

### launchd (macOS 권장)

`~/Library/LaunchAgents/com.blogcrawler.daily.plist` 파일 생성:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.blogcrawler.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/blog_crawler.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

```bash
# 등록
launchctl load ~/Library/LaunchAgents/com.blogcrawler.daily.plist

# 확인
launchctl list | grep blogcrawler
```

## 🛠 문제 해결

### "No new posts" - 새 포스트가 없어요

**원인**: 이미 모든 포스트를 수집했거나, 새 글이 없음

**해결**:
```bash
# 블로그에 실제로 새 글이 있는지 확인
python blog_manager.py list --verbose

# 특정 블로그 강제 재수집 (limit 높이기)
python blog_crawler.py --blog-id 1 --limit 50
```

### "Feed parsing failed" - 피드 파싱 실패

**원인**: RSS 피드가 변경되었거나 접근 불가

**해결**:
```bash
# RSS 피드 유효성 재검사
python blog_manager.py validate --verbose

# 실패한 블로그의 feed_url 수정
# blogs_list.csv에서 해당 블로그의 feed_url 업데이트 후
python blog_manager.py load --csv blogs_list.csv
```

### 요약이 이상해요

**원인**: HTML 태그가 많거나 특수 문자 포함

**개선 방법**:
1. 현재는 단순히 200자 자르기
2. 향후 AI 요약으로 업그레이드 가능:

```bash
# OpenAI API 사용 (향후 추가 예정)
python blog_crawler.py --use-ai --api-key sk-...
```

### 크롤링이 너무 느려요

**해결**:
```bash
# Rate limiting 시간 줄이기 (blog_crawler.py 수정)
# 76번째 줄: time.sleep(2) → time.sleep(1)

# 또는 병렬 처리 (향후 추가)
```

## 📈 성능 최적화

### 현재 성능
- 11개 블로그 × 10개 포스트 = 110개 수집 시간: **약 30-40초**
- Rate limiting 2초 포함
- 네트워크 상태에 따라 변동

### 100개 블로그 예상
- 100개 블로그 × 10개 = 1000개 포스트
- 예상 시간: **약 4-5분**
- 하루 1회 실행으로 충분

## 🎨 활용 예시

### 1. 카테고리별 최신 글 확인

```bash
# ML 카테고리만
sqlite3 blogs.db "SELECT p.title, b.name FROM posts p JOIN blogs b ON p.blog_id = b.id WHERE b.category = 'ml' ORDER BY p.scraped_at DESC LIMIT 10;"
```

### 2. 특정 키워드 검색

```bash
# 'AI' 포함 포스트
sqlite3 blogs.db "SELECT title, url FROM posts WHERE title LIKE '%AI%' OR summary LIKE '%AI%';"
```

### 3. 오늘 수집된 포스트만

```bash
sqlite3 blogs.db "SELECT COUNT(*) FROM posts WHERE DATE(scraped_at) = DATE('now');"
```

## 🔮 다음 단계 (Phase 2)

### 1. AI 요약 시스템
```python
# OpenAI GPT-4-mini 사용
summary = openai.ChatCompletion.create(
    model="gpt-4-mini",
    messages=[{"role": "user", "content": f"다음 글을 2-3문장으로 요약: {content}"}]
)
```

**비용**: 1000개 포스트 약 $1-2

### 2. 웹 프론트엔드
- React + FastAPI
- 타임라인 뷰
- 검색 및 필터
- 북마크 기능

### 3. 자동 스케줄링
- Celery + Redis
- 우선순위별 크롤링 주기
- 실패 재시도

### 4. 알림 시스템
- 새 포스트 이메일 다이제스트
- 특정 키워드 알림
- 주간 요약 리포트

## 📊 실전 데이터 예시

현재 수집된 50개 포스트:
```
카테고리별 분포:
- ml: 5개 (10%)
- data: 5개 (10%)
- essay: 5개 (10%)
- other: 35개 (70%)

주제별 분포:
- 주식/투자: 20개 (40%)
- AI/기술: 15개 (30%)
- 여행: 10개 (20%)
- 기타: 5개 (10%)
```

## 💡 사용 팁

### Tip 1: 새 블로그 추가 후 즉시 크롤링
```bash
# 새 블로그 추가
python blog_auto_tagger.py https://new-blog.com
python blog_manager.py load --csv analyzed_blogs.csv

# 방금 추가한 블로그 ID 확인
python blog_manager.py list

# 해당 블로그만 크롤링
python blog_crawler.py --blog-id 12 --verbose
```

### Tip 2: 백업
```bash
# 매주 DB 백업
cp blogs.db "blogs_backup_$(date +%Y%m%d).db"

# 또는 CSV로 내보내기
python blog_manager.py export --csv blogs_backup.csv
```

### Tip 3: 테스트용 소규모 실행
```bash
# 먼저 1개 블로그만 테스트
python blog_crawler.py --blog-id 1 --limit 3 --verbose

# 문제 없으면 전체 실행
python blog_crawler.py
```

## 📞 지원

### 로그 확인
크롤러는 오류를 콘솔에 출력합니다:
```bash
# 로그 파일로 저장
python blog_crawler.py --verbose > crawler.log 2>&1
```

### 일반적인 이슈

**Q: 중복 포스트가 계속 수집돼요**
A: URL이 조금씩 다를 수 있습니다 (쿼리 파라미터 등). DB에서 확인:
```bash
sqlite3 blogs.db "SELECT url FROM posts WHERE title LIKE '%제목%';"
```

**Q: 특정 블로그만 계속 실패해요**
A: 해당 블로그를 비활성화:
```bash
sqlite3 blogs.db "UPDATE blogs SET active = FALSE WHERE id = 5;"
```

**Q: 100개 블로그를 추가하면 느려질까요?**
A: Rate limiting이 있어 시간이 비례합니다. 대신:
- 우선순위별로 나눠서 실행
- 병렬 처리 (향후 추가)
- 스케줄링으로 분산

---

**버전**: 1.0
**업데이트**: 2024-02-23
**다음 업데이트**: AI 요약 시스템 추가 예정
