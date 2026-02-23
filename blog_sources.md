# 블로그 100개 수집 가이드

## 🎯 카테고리별 목표 분배

- **Machine Learning** (30개): AI, 딥러닝, ML 엔지니어링
- **Art & Design** (20개): 디자인, 일러스트, 창작
- **Tech & Programming** (25개): 개발, 웹, 시스템
- **Data Science** (15개): 데이터 분석, 시각화
- **Essay & Others** (10개): 에세이, 생각, 일상

## 📚 추천 블로그 소스

### Machine Learning (30개)

#### 대기업/연구소 블로그 (10개)
- https://openai.com/blog
- https://www.deepmind.com/blog
- https://ai.googleblog.com
- https://ai.meta.com/blog
- https://www.microsoft.com/en-us/research/blog
- https://research.nvidia.com/blog
- https://aws.amazon.com/blogs/machine-learning
- https://engineering.fb.com
- https://blog.tensorflow.org
- https://blog.pytorch.org

#### 개인 블로그/미디엄 (10개)
- https://karpathy.github.io
- https://colah.github.io
- https://ruder.io
- https://lilianweng.github.io
- https://distill.pub
- https://thegradient.pub
- https://machinelearningmastery.com
- https://sebastianruder.com
- https://www.fast.ai/blog
- https://huggingface.co/blog

#### 한국 ML 블로그 (10개)
- https://blog.est.ai
- https://brunch.co.kr/@kakao-it (카카오 AI)
- https://tech.kakaoenterprise.com
- https://www.upstage.ai/blog
- https://www.tensorflow.blog (텐서 플로우 한국어)
- 네이버 블로그에서 "머신러닝" 검색 → 인기 블로그 5-10개

### Art & Design (20개)

#### 디지털 아트/디자인 (10개)
- https://www.creativeapplications.net
- https://www.thisiscolossal.com
- https://www.itsnicethat.com
- https://www.designboom.com
- https://www.awwwards.com/blog
- https://www.creativebloq.com
- https://99designs.com/blog
- https://dribbble.com/stories
- https://www.behance.net/blogs
- https://eyeondesign.aiga.org

#### 한국 디자인 블로그 (10개)
- 브런치에서 "디자인" 검색 → 인기 작가 10명
- 네이버 블로그에서 "UX 디자인", "일러스트" 검색

### Tech & Programming (25개)

#### 웹 개발 (10개)
- https://www.smashingmagazine.com
- https://css-tricks.com
- https://alistapart.com
- https://web.dev
- https://blog.logrocket.com
- https://dev.to (인기 작가)
- https://kentcdodds.com/blog
- https://overreacted.io
- https://joshwcomeau.com
- https://2ality.com

#### 일반 프로그래밍 (10개)
- https://martinfowler.com
- https://www.joelonsoftware.com
- https://blog.codinghorror.com
- https://increment.com
- https://www.thoughtworks.com/insights
- https://stackoverflow.blog
- https://github.blog
- https://www.paulgraham.com/articles.html
- https://blog.cleancoder.com
- https://danluu.com

#### 한국 개발 블로그 (5개)
- https://techblog.woowahan.com (우아한형제들)
- https://tech.kakao.com
- https://engineering.linecorp.com/ko/blog
- https://meetup.toast.com
- 브런치/네이버에서 개발자 블로그 검색

### Data Science (15개)

#### 데이터 분석/시각화 (10개)
- https://flowingdata.com
- https://fivethirtyeight.com
- https://simplystatistics.org
- https://www.dataquest.io/blog
- https://towardsdatascience.com
- https://www.tableau.com/blog
- https://mode.com/blog
- https://www.kdnuggets.com
- https://blog.datasciencedojo.com
- https://www.analyticsvidhya.com/blog

#### 한국 데이터 블로그 (5개)
- 브런치/네이버에서 "데이터 분석", "데이터 사이언스" 검색

### Essay & Others (10개)

#### 에세이/생각 (10개)
- https://waitbutwhy.com
- https://www.brainpickings.org
- https://fs.blog
- https://www.gwern.net
- 브런치 인기 작가 6-7명
- 네이버 블로그 에세이 작가 2-3명

## 🔍 블로그 찾는 법

### 1. Feedly 활용
```
1. Feedly.com 접속
2. 주제 검색 (예: "machine learning")
3. "Sources" 탭 → 인기 블로그 확인
4. RSS 피드 URL 복사
```

### 2. GitHub Awesome Lists
```
검색: "awesome machine learning blogs github"
예시: https://github.com/josephmisiti/awesome-machine-learning
      → 블로그 섹션 확인
```

### 3. Medium Publications
```
Medium 인기 Publications:
- Towards Data Science
- Better Programming
- UX Collective
- The Startup
→ 각 Publication URL 추가
```

### 4. 한국 플랫폼
```
브런치:
- 브런치 메인 → "IT·기술" 카테고리
- 인기 작가 리스트 → @username URL

네이버 블로그:
- 관심 주제 검색
- "이웃 블로그" 많은 블로그 = 인기 블로그
```

## 📝 URL 정리 팁

### blog_urls.txt 형식
```
# Machine Learning
https://openai.com/blog
https://www.deepmind.com/blog
https://karpathy.github.io

# Art & Design
https://www.thisiscolossal.com
https://www.itsnicethat.com

# Tech
https://www.smashingmagazine.com
https://css-tricks.com
```

주석(#)으로 카테고리 구분하면 관리 편함!

## ⚡ 빠른 수집 전략

**목표: 1시간 안에 100개 수집**

1. **30분**: 위 리스트에서 복붙 (60개)
2. **15분**: Feedly에서 추가 검색 (20개)
3. **15분**: 브런치/네이버 블로그 (20개)

## 🎯 다음 단계

수집 완료 후:
```bash
# 자동 분석
python blog_auto_tagger.py --file blog_urls.txt

# DB 로드
python blog_manager.py load --csv analyzed_blogs.csv

# 검증
python blog_manager.py validate

# 크롤링
python blog_crawler.py --limit 10
```
