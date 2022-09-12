from abc import ABCMeta
from typing import Generator

from scrapy import Request

from spiders.NewsSpider import NewsSpider
from utils import get_now_dt_str


class LSDSpider(NewsSpider, metaclass=ABCMeta):
    name: str = "LSDSpider"

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        sid: str = "100",
        **kwargs
    ):
        super().__init__(date, join_char, **kwargs)
        self.list_url: str = (
            "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&listType=title"
            "&sid1={sid1}&date={date}&page={page}"
        )
        self.article_url: str = "https://n.news.naver.com/mnews/article/{oid}/{aid}"
        self.sid: str = sid

    def start_requests(self) -> Generator[Request, None, None]:
        yield Request(
            url=self.list_url.format(sid1=self.sid, date=self.date, page=1),
            callback=self.parse_list,
        )
