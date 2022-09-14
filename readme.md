## Scrapy 기반 Naver 뉴스 수집기
[![codecov](https://codecov.io/gh/Damien-IR/naver_news_scraper/branch/master/graph/badge.svg?token=A799P1WGNH)](https://codecov.io/gh/Damien-IR/naver_news_scraper)

### 사용법

자세한 Scrapy 사용법은 [Scrapy 공식 문서](https://docs.scrapy.org/en/latest/intro/tutorial.html)가 도움이 되실 것입니다.

- sid는 네이버에서 사용하는 분류의 id로서, 각 뉴스에서 내부적으로 사용하는 분류입니다.
- 아래는 많이 사용하는 대분류입니다.
  * 정치 = 100
  * 경제 = 101
  * 사회 = 102
  * 생활/문화 = 103
  * 세계 = 104
  * IT/과학 = 105
  * 연예 = 106
  * 스포츠 = 107
- 그 외 소분류는 너무 많으므로 생략합니다.


- 각 Spider 가 입력받을 수 있는 파라미터는 다음과 같습니다.
- `NewsSpider` : `date` (str), `join_char` (str)
- `LSDSpider`, `EntSpider`, `SportSpider` : `sid` (str), `date` (str), `join_char` (str)

아래는 본 프로젝트에서 실행 가능한 crawl 명령어 목록입니다.
- 모든 카테고리 뉴스 수집 : `scrapy crawl NewsSpider [-a date=날짜(%Y%m%d 형식)] [-a join_char=줄 바꿈 구분자]`
- 일반 카테고리 뉴스 수집 : `scrapy crawl LSDSpider [-a sid=카테고리입력(예: 100, 101...)] [-a date=날짜(%Y%m%d 형식)] [-a join_char=줄 바꿈 구분자]`
- 연예 뉴스 수집 : `scrapy crawl EntSpider [-a sid=카테고리입력] [-a date=날짜(%Y%m%d 형식] [-a join_char=줄 바꿈 구분자]`
- 스포츠 뉴스 수집 : `scrapy crawl SportSpider [-a sid=카테고리입력] [-a date=날짜(%Y%m%d 형식] [-a join_char=줄 바꿈 구분자]`

### FAQ
- 왜 연예 / 스포츠 뉴스용 수집기가 별도로 구분되어 있나요?
  * 연예 / 스포츠 뉴스는 일반적인 방법으로 접근 시 sid 데이터가 제공되지 않고, 별도의 경로("entertain.naver.com", "sports.naver.com") 로 리다이렉션 처리 되기 때문에 이를 막기 위함입니다.
- 왜 `join_char` 파라미터가 있나요?
  * 네이버 뉴스는 기사 내용이 여러 줄로 구성되어 있습니다. 이를 하나의 문자열로 만들기 위해 `join_char` 파라미터를 사용합니다. 이를 띄어쓰기를 사용하는 경우 여러 애로사항이 있을 수 있어 수정 가능하도록 하였습니다.