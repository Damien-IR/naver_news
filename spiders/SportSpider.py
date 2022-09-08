from abc import ABCMeta
from typing import Generator

import scrapy
from scrapy.http import Response

from items import NewsItem
from spiders.EntSpider import EntSpider


class SportSpider(EntSpider, metaclass=ABCMeta):
    name = 'SportSpider'

    def extract_article_item(self, article_res: Response) -> NewsItem:
        item: NewsItem = super().extract_article_item(article_res)
        item.url = "https://sports.news.naver.com/news?oid={oid}&aid={aid}".format(oid=item.oid, aid=item.aid)
        return item

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        yield scrapy.Request(url=self.list_url.format(sid1="107", date=self.date, page=1), callback=self.parse_list)
