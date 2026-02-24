# 블로그 자동 태그 생성기 🏷️

블로그 URL만 입력하면 자동으로 다음을 추출합니다:
- 블로그 이름
- RSS 피드 URL
- 카테고리 (ml, art, tech, data, essay)
- 태그 (최대 5개)
- 설명

## 🚀 빠른 시작

### 설치

```bash
# 필수 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install requests beautifulsoup4 lxml
```

### 사용법

#### 방법 1: 단일 URL 분석

```bash
python blog_auto_tagger.py https://openai.com/blog
```

출력 예시:
```
🔍 분석 중: https://openai.com/blog
✅ 완료: OpenAI Blog

============================================================
📊 분석 결과
============================================================
blog_name      : OpenAI Blog
url            : https://openai.com/blog
feed_url       : https://openai.com/blog/rss
category       : ml
priority       : medium
active         : true
description    : OpenAI's mission is to ensure that artificial general intelligence...
tags           : ai,machine-learning,research,gpt,deep-learning
============================================================
```

#### 방법 2: 여러 URL 한 번에 분석

```bash
# 명령줄에서 직접
python blog_auto_tagger.py https://openai.com/blog https://www.thisiscolossal.com

# 파일에서 읽기
python blog_auto_tagger.py --file blog_urls.txt --output my_blogs.csv
```

#### 방법 3: 대화형 모드

```bash
python blog_auto_tagger.py

# URL을 하나씩 입력하고, 완료하려면 빈 줄 입력
```

## 📋 출력 형식

분석 결과는 CSV 파일로 저장됩니다:

```csv
blog_name,url,feed_url,category,priority,active,description,tags
"OpenAI Blog","https://openai.com/blog","https://openai.com/blog/rss","ml","medium","true","OpenAI official blog","ai,research,gpt,machine-learning,deep-learning"
```

이 CSV는 바로 `blog_manager.py`로 로드할 수 있습니다:

```bash
python blog_manager.py load --csv analyzed_blogs.csv
```

## 🤖 AI 모드 (선택 사항)

더 정확한 분석을 원하면 OpenAI API를 사용할 수 있습니다:

```bash
# OpenAI 패키지 설치
pip install openai

# AI 모드로 실행
python blog_auto_tagger.py --ai --api-key sk-YOUR-API-KEY https://example.com

# 또는 실행 중에 입력
python blog_auto_tagger.py --ai https://example.com
# 프롬프트에서 API 키 입력
```

### AI vs 키워드 모드 비교

| 특징 | 키워드 모드 (기본) | AI 모드 |
|------|------------------|---------|
| 비용 | 무료 | $0.0001/블로그 |
| 정확도 | 70-80% | 90-95% |
| 속도 | 빠름 (1-2초) | 느림 (3-5초) |
| 의존성 | 없음 | OpenAI API 필요 |

**추천**: 먼저 키워드 모드로 100개를 분석하고, 애매한 것만 AI 모드로 재분석

## 📁 파일에서 일괄 처리

`blog_urls.txt` 파일 형식:

```
# Machine Learning 블로그
https://openai.com/blog
https://www.deepmind.com/blog

# Art 블로그
https://www.thisiscolossal.com
https://www.itsnicethat.com
```

실행:

```bash
python blog_auto_tagger.py --file blog_urls.txt --output ml_art_blogs.csv
```

## 🎯 100개 블로그 빠르게 채우기

### 워크플로우

1. **URL 수집** (10분)
   ```bash
   # 관심 주제로 검색
   # "best machine learning blogs"
   # "top art design blogs"
   # URL을 blog_urls.txt에 복붙
   ```

2. **자동 분석** (5분)
   ```bash
   python blog_auto_tagger.py --file blog_urls.txt
   ```

3. **결과 확인 및 수정** (10분)
   ```bash
   # analyzed_blogs.csv 파일을 열어서
   # 잘못 분류된 것만 수정
   ```

4. **DB에 로드** (1분)
   ```bash
   python blog_manager.py load --csv analyzed_blogs.csv
   python blog_manager.py stats
   ```

**총 소요 시간: 약 30분으로 100개 완성!**

## 🔧 추출 방식

### 1. 블로그 이름
- `<title>` 태그
- Open Graph `og:site_name`
- 도메인 이름

### 2. RSS 피드
자동으로 다음 경로를 확인:
- `/feed`
- `/rss`
- `/feed.xml`
- `/rss.xml`
- `/atom.xml`
- `/blog/feed`

### 3. 카테고리 분류

키워드 매칭 기반:

```python
ml: machine learning, deep learning, ai, neural network...
art: art, design, creative, illustration, painting...
tech: technology, programming, software, developer...
data: data, analytics, statistics, visualization...
essay: essay, thought, opinion, writing, life...
```

### 4. 태그 추출

1. 페이지 텍스트 분석
2. 빈도수가 높은 단어 추출
3. 불용어 제거
4. 카테고리 키워드 우선
5. 상위 5개 선택

## 💡 팁과 트릭

### RSS 피드가 없는 블로그

자동으로 일반적인 경로를 시도하지만, 찾지 못하면:

```bash
# 직접 찾기
# 1. 브라우저에서 페이지 소스 보기 (Ctrl+U)
# 2. "rss" 또는 "feed" 검색
# 3. 수동으로 CSV에 추가
```

### 카테고리가 잘못 분류된 경우

```bash
# analyzed_blogs.csv를 열어서 직접 수정
# art → ml로 변경 등
```

### 100개를 카테고리별로 나누기

```bash
# ML 블로그만 먼저
python blog_auto_tagger.py --file ml_urls.txt --output ml_blogs.csv

# Art 블로그
python blog_auto_tagger.py --file art_urls.txt --output art_blogs.csv

# 나중에 합치기
python blog_manager.py load --csv ml_blogs.csv
python blog_manager.py load --csv art_blogs.csv
```

## 🚨 주의사항

### Rate Limiting

너무 많은 요청을 빠르게 보내면 차단될 수 있습니다:

```python
# 스크립트 수정 (필요 시)
import time

for url in urls:
    result = tagger.analyze_blog(url)
    time.sleep(2)  # 2초 대기
```

### 프라이버시

- User-Agent를 명시하여 정상 브라우저임을 표시
- robots.txt를 준수
- 개인 블로그는 과도한 크롤링 자제

## 🔍 문제 해결

### "Connection timeout" 오류

```bash
# 타임아웃 증가
# blog_auto_tagger.py 15번째 줄 수정
# timeout=15 → timeout=30
```

### "No module named 'bs4'" 오류

```bash
pip install beautifulsoup4
```

### SSL 인증서 오류

```python
# blog_auto_tagger.py에서
requests.get(url, verify=False)  # 비추천, 보안 위험
```

## 📊 실전 예시

### 예시 1: 유명 ML 블로그 10개

```bash
echo "https://openai.com/blog
https://www.deepmind.com/blog
https://ai.googleblog.com
https://ai.meta.com/blog
https://machinelearningmastery.com
https://distill.pub
https://thegradient.pub
https://ruder.io
https://karpathy.github.io
https://colah.github.io" > ml_blogs.txt

python blog_auto_tagger.py --file ml_blogs.txt --output ml_analyzed.csv
```

### 예시 2: 디자인 블로그 10개

```bash
python blog_auto_tagger.py \
  https://www.awwwards.com/blog \
  https://www.smashingmagazine.com \
  https://www.itsnicethat.com \
  https://www.thisiscolossal.com \
  --output design_blogs.csv
```

### 예시 3: CSV 결과 바로 로드

```bash
python blog_auto_tagger.py --file blog_urls.txt && \
python blog_manager.py load --csv analyzed_blogs.csv && \
python blog_manager.py stats
```

## 🎨 Python에서 사용

```python
from blog_auto_tagger import BlogAutoTagger, analyze_multiple_blogs

# 단일 분석
tagger = BlogAutoTagger()
result = tagger.analyze_blog('https://openai.com/blog')
print(result['tags'])  # 'ai,machine-learning,research,gpt,neural-network'

# 여러 개 분석
urls = [
    'https://openai.com/blog',
    'https://www.thisiscolossal.com',
    'https://techcrunch.com'
]
results = analyze_multiple_blogs(urls, output_csv='my_blogs.csv')

# AI 모드
tagger_ai = BlogAutoTagger(use_ai=True, api_key='sk-...')
result = tagger_ai.analyze_blog('https://example.com')
```

## 📈 다음 단계

자동 태그 생성 후:

1. ✅ **검증**: `python blog_manager.py validate`
2. ✅ **통계**: `python blog_manager.py stats`
3. ➡️ **크롤러 개발**: 실제 콘텐츠 수집 시작
4. ➡️ **요약 시스템**: AI 요약 엔진 구축

---

**버전**: 1.0
**업데이트**: 2024-02-23
