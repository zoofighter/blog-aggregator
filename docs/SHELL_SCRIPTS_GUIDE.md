# Shell Script 가이드 (.sh 파일) 🔧

## 🤔 Shell Script란?

**Shell Script** = Bash 명령어를 모아둔 자동화 스크립트

Python의 `.py` 파일처럼, `.sh` 파일은 **터미널 명령어를 자동으로 실행**합니다.

---

## 📦 프로젝트의 Shell Scripts

### 현재 스크립트 목록

```bash
scripts/
├── quick_setup.sh       # 🚀 전체 프로젝트 자동 설정
├── setup_postgres.sh    # 🐘 PostgreSQL 설정
├── setup_scheduler.sh   # ⏰ 자동 스케줄링 설정
└── backup.sh            # 💾 데이터베이스 백업
```

---

## 🎯 각 스크립트 용도

### 1. **quick_setup.sh** - 프로젝트 초기 설정

**실행**:
```bash
./scripts/quick_setup.sh
```

**수행 작업**:
1. ✅ PostgreSQL 설치 확인
2. ✅ DB 타입 선택 (SQLite/PostgreSQL)
3. ✅ 비밀번호 설정
4. ✅ .env 파일 생성
5. ✅ Python 패키지 설치
6. ✅ 데이터베이스 초기화

**이 스크립트 없이 수동으로 하면?**
```bash
# 최소 50줄 이상의 명령어를 순서대로 입력해야 함
brew install postgresql@15
brew services start postgresql@15
createdb blog_aggregator
echo "DB_TYPE=postgresql" > .env
echo "DB_HOST=localhost" >> .env
echo "DB_PORT=5432" >> .env
echo "DB_NAME=blog_aggregator" >> .env
echo "DB_USER=postgres" >> .env
read -p "비밀번호: " PASSWORD
echo "DB_PASSWORD=$PASSWORD" >> .env
chmod 600 .env
pip install psycopg2-binary
export $(cat .env | xargs)
python -c "from db_config import get_db_config; get_db_config().init_database()"
# ... 계속 ...
```

**스크립트를 사용하면?**
```bash
./scripts/quick_setup.sh
# 끝! 자동으로 모든 작업 완료
```

---

### 2. **setup_postgres.sh** - PostgreSQL 전용

**실행**:
```bash
./scripts/setup_postgres.sh
```

**수행 작업**:
1. ✅ PostgreSQL 실행 확인
2. ✅ 데이터베이스 생성
3. ✅ .env 파일 구성
4. ✅ SQLite → PostgreSQL 마이그레이션

**언제 사용?**
- PostgreSQL로 업그레이드할 때
- 데이터베이스를 재설정할 때

---

### 3. **setup_scheduler.sh** - 자동 스케줄링

**실행**:
```bash
./scripts/setup_scheduler.sh
```

**수행 작업**:
1. ✅ LaunchAgents 설정
2. ✅ 매일 오전 9시, 오후 6시 자동 크롤링
3. ✅ 로그 파일 설정

**결과**: 자동으로 매일 포스트 수집

---

### 4. **backup.sh** - 데이터베이스 백업

**실행**:
```bash
./scripts/backup.sh
```

**수행 작업**:
1. ✅ blogs.db → backups/에 복사
2. ✅ 날짜 포맷으로 저장
3. ✅ 30일 이상 된 백업 자동 삭제

**출력 예시**:
```
💾 데이터베이스 백업 시작...
✅ 백업 완료: backups/blogs_backup_20240224_103045.db
120K backups/blogs_backup_20240224_103045.db

🧹 오래된 백업 정리 중...
✅ 30일 이상 된 백업 삭제 완료

📋 현재 백업 목록:
-rw-r--r--  1 boon  staff  120K Feb 24 10:30 backups/blogs_backup_20240224_103045.db
```

---

## 🆚 Python vs Shell Script 비교

| 작업 | Python | Shell Script | 승자 |
|------|--------|--------------|------|
| **파일 이동** | `shutil.move()` | `mv file.txt dest/` | .sh ✅ |
| **권한 설정** | `os.chmod()` | `chmod +x file.sh` | .sh ✅ |
| **환경 변수** | `os.environ['VAR']` | `export VAR=value` | .sh ✅ |
| **패키지 설치** | 불가능 | `pip install package` | .sh ✅ |
| **데이터 처리** | Pandas 등 | 제한적 | .py ✅ |
| **복잡한 로직** | 객체지향 | 제한적 | .py ✅ |

**결론**:
- 🔧 **시스템 설정, 자동화** → Shell Script
- 🐍 **데이터 처리, 복잡한 로직** → Python

---

## 📝 Shell Script 기본 문법

### 1. 시작 (Shebang)

```bash
#!/bin/bash
# 이 줄이 반드시 첫 줄에 있어야 함
```

### 2. 변수

```bash
# 변수 선언
NAME="Blog Aggregator"
DATE=$(date +%Y%m%d)

# 변수 사용
echo "프로젝트: $NAME"
echo "날짜: $DATE"
```

### 3. 조건문

```bash
if [ -f "blogs.db" ]; then
    echo "데이터베이스 존재함"
else
    echo "데이터베이스 없음"
fi
```

### 4. 반복문

```bash
# 파일 목록 순회
for file in *.csv; do
    echo "처리 중: $file"
done
```

### 5. 사용자 입력

```bash
read -p "이름을 입력하세요: " NAME
echo "안녕하세요, $NAME님!"
```

### 6. 색상 출력

```bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}✅ 성공${NC}"
echo -e "${RED}❌ 실패${NC}"
```

---

## 🎯 실전 예시

### 예시 1: 일일 크롤링 스크립트

```bash
#!/bin/bash
# daily_crawl.sh

echo "🚀 일일 크롤링 시작..."

# 프로젝트 경로로 이동
cd /Users/boon/Dropbox/03_code/0223_a

# 크롤링 실행
python blog_crawler_parallel.py --limit 10

# 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ 크롤링 성공"
    python blog_manager.py post-stats
else
    echo "❌ 크롤링 실패"
    exit 1
fi
```

**사용**:
```bash
chmod +x scripts/daily_crawl.sh
./scripts/daily_crawl.sh
```

---

### 예시 2: 통계 이메일 발송

```bash
#!/bin/bash
# send_stats.sh

echo "📊 통계 이메일 발송..."

# 프로젝트 경로
cd /Users/boon/Dropbox/03_code/0223_a

# 환경 변수 로드
export $(cat .env | grep -v '^#' | xargs)

# 다이제스트 생성 및 발송
python email_digest.py \
    --days 7 \
    --send \
    --to-email your@email.com \
    --from-email $SMTP_EMAIL \
    --password $SMTP_PASSWORD

echo "✅ 이메일 발송 완료"
```

---

### 예시 3: 개발/프로덕션 전환

```bash
#!/bin/bash
# switch_env.sh

if [ "$1" = "dev" ]; then
    echo "🔧 개발 환경으로 전환"
    export DB_TYPE=sqlite
    export DB_PATH=blogs_dev.db
elif [ "$1" = "prod" ]; then
    echo "🚀 프로덕션 환경으로 전환"
    export DB_TYPE=postgresql
    export DB_HOST=localhost
    export DB_NAME=blog_aggregator
else
    echo "사용법: ./switch_env.sh [dev|prod]"
    exit 1
fi

# 앱 실행
python app_v2.py
```

**사용**:
```bash
./scripts/switch_env.sh dev   # 개발
./scripts/switch_env.sh prod  # 프로덕션
```

---

## 🛠️ Shell Script 작성 팁

### 1. 에러 처리

```bash
# 에러 발생 시 즉시 종료
set -e

# 실패한 명령어 추적
set -x
```

### 2. 경로 안전하게 처리

```bash
# 현재 스크립트 위치
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 프로젝트 루트로 이동
cd "$SCRIPT_DIR/.."
```

### 3. 디버깅

```bash
# 디버그 모드 실행
bash -x script.sh

# 또는 스크립트 내부에
set -x  # 디버깅 시작
# ... 명령어 ...
set +x  # 디버깅 종료
```

### 4. 로그 남기기

```bash
# 로그 파일에 저장
./scripts/backup.sh >> logs/backup.log 2>&1

# 화면과 파일 동시 출력
./scripts/backup.sh 2>&1 | tee logs/backup.log
```

---

## 📱 Shell Script 실행 방법

### 방법 1: 실행 권한 부여

```bash
# 권한 부여
chmod +x scripts/backup.sh

# 실행
./scripts/backup.sh
```

### 방법 2: bash 명령어 사용

```bash
# 권한 없이 실행
bash scripts/backup.sh
```

### 방법 3: source 명령어 (환경 변수 유지)

```bash
# 환경 변수를 현재 셸에 적용
source scripts/setup_env.sh

# 또는
. scripts/setup_env.sh
```

---

## ⏰ 자동 실행 (Cron)

### cron으로 스케줄링

```bash
# cron 편집
crontab -e

# 추가할 내용
# 매일 오전 9시 크롤링
0 9 * * * /Users/boon/Dropbox/03_code/0223_a/scripts/daily_crawl.sh

# 매일 오후 7시 백업
0 19 * * * /Users/boon/Dropbox/03_code/0223_a/scripts/backup.sh

# 매주 일요일 오전 3시 통계 이메일
0 3 * * 0 /Users/boon/Dropbox/03_code/0223_a/scripts/send_stats.sh
```

---

## 🐛 문제 해결

### "Permission denied" 에러

```bash
# 원인: 실행 권한 없음
# 해결:
chmod +x scripts/your_script.sh
```

### "command not found" 에러

```bash
# 원인: Python 경로 문제
# 해결: 절대 경로 사용
/opt/anaconda3/bin/python script.py

# 또는 which로 경로 확인
which python3
# 결과를 스크립트에 사용
```

### 환경 변수가 안 보일 때

```bash
# source 사용
source .env

# 또는
export $(cat .env | xargs)
```

---

## 💡 Shell Script vs Python 선택 가이드

### Shell Script 사용 ✅

1. **시스템 명령 실행**
   - 파일 이동, 복사, 삭제
   - 권한 설정
   - 패키지 설치

2. **간단한 자동화**
   - 백업
   - 로그 정리
   - 배포

3. **환경 설정**
   - 환경 변수 설정
   - 프로세스 시작/중지

### Python 사용 ✅

1. **복잡한 로직**
   - 데이터 분석
   - API 호출
   - 조건부 처리

2. **크로스 플랫폼**
   - Windows, macOS, Linux 모두 지원

3. **라이브러리 활용**
   - Pandas, Requests 등

---

## 📚 더 배우기

### 추천 자료

- [Bash Scripting Tutorial](https://www.shellscript.sh/)
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/)

### 프로젝트 내 예시

- `scripts/quick_setup.sh` - 전체 설정 예시
- `scripts/backup.sh` - 백업 자동화 예시

---

## ✅ 요약

| 질문 | 답변 |
|------|------|
| **왜 .sh 파일을 쓰나요?** | 여러 명령어를 한 번에 자동 실행 |
| **언제 사용하나요?** | 시스템 설정, 백업, 배포 등 |
| **Python과 차이는?** | 시스템 명령 실행이 더 쉬움 |
| **어떻게 만드나요?** | `#!/bin/bash`로 시작, 명령어 작성 |
| **어떻게 실행하나요?** | `chmod +x script.sh` → `./script.sh` |

**Shell Script = 반복 작업을 자동화하는 강력한 도구!** 🚀
