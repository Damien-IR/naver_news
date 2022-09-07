from abc import ABCMeta
from datetime import datetime
from typing import List, Generator, Dict
from urllib.parse import parse_qs, urlparse

import scrapy
from scrapy.http import Response

from spiders.NewsSpider import NewsSpider


class EntSpider(NewsSpider, metaclass=ABCMeta):
    name = 'EntSpider'

    def __init__(self, date: str = datetime.now().strftime("%Y%m%d"), join_char: str = "\n", **kwargs):
        super().__init__(date, join_char, **kwargs)
        self.list_url: str = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&listType=title" \
                             "&sid1={sid1}&date={date}&page={page}"
        self.article_url: str = "https://n.news.naver.com/entertain/article/{oid}/{aid}"

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        yield scrapy.Request(url=self.list_url.format(sid1="106", date=self.date, page=1), callback=self.parse_list)

    def extract_article_links(self, list_res: Response) -> List[str]:
        link_list: List[str] = list_res.css("div.list_body ul.type02 li a::attr(href)").getall()

        def convert_url(url: str) -> str:
            if "oid" not in url or "aid" not in url:
                if "mnews" in url:
                    url = url.replace("mnews", "entertain")
                    return url.split("?")[0] if "?" in url else url
            else:
                parsed_url: urlparse = urlparse(url)
                query_dict: Dict = parse_qs(parsed_url.query)
                oid: str = query_dict["oid"][0]
                aid: str = query_dict["aid"][0]
                return self.article_url.format(oid=oid, aid=aid)

        return list(map(convert_url, link_list))
