BOT_NAME = "naver_news"
SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"

USER_AGENT = "Spider for Naver News"
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 10
TELNETCONSOLE_ENABLED = False
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
