import json
import re
from abc import ABCMeta
from collections.abc import Iterable
from datetime import datetime
from typing import Generator, Optional, List, Dict

import scrapy
from scrapy.http import Request, Response

from items import NewsItem


class NewsSpider(scrapy.Spider, metaclass=ABCMeta):
    name: str = 'NewsSpider'
    allowed_domains: List[str] = ['naver.com']

    def __init__(self, date: str = datetime.now().strftime("%Y%m%d"), join_char: str = "\n", **kwargs):
        super().__init__(**kwargs)
        self.date: str = date
        self.join_char: str = join_char
        self.list_url: str = "https://news.naver.com/main/list.naver?mode=LS2D&mid=sec&listType=title&" \
                             "date={date}&page={page}"

        self.re_article_ptrn: re.Pattern = re.compile(r"var article = (\{[^;]+});")
        self.re_office_ptrn: re.Pattern = re.compile(r"var office = (\{[^;]+});")

    @staticmethod
    def strptime_util(
            datetime_str: str,
            fmt: str = "%Y.%m.%d. %p %I:%M",
            replace_dict: Optional[Dict] = None
    ) -> datetime:
        if not replace_dict:
            replace_dict: Dict = {
                "오전": "AM",
                "오후": "PM"
            }
        for key, value in replace_dict.items():
            datetime_str = datetime_str.replace(key, value)
        return datetime.strptime(datetime_str, fmt)

    @staticmethod
    def strftime_util(datetime_obj: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime_obj.strftime(fmt)

    @staticmethod
    def strip_and_filter_str_list(str_list: list[str]) -> list[str]:
        return list(filter(lambda x: x != "", map(lambda x: x.strip(), str_list)))

    @staticmethod
    def js_object_to_json(js_object: str, remove_str_iter: Optional[Iterable[str]] = None) -> str:
        result: str = re.sub(r'(\w+)\s*:', r'"\1":', js_object)
        if remove_str_iter:
            for string in remove_str_iter:
                result = result.replace(string, '""')
        return result

    @staticmethod
    def extract_article_links(list_res: Response) -> List[str]:
        return list_res.css("div.list_body ul.type02 li a::attr(href)").getall()

    @staticmethod
    def extract_pages(list_res: Response) -> List[str]:
        other_pages: List[str] = list_res.css("div.paging a::attr(href)").getall()
        return list(map(lambda x: "https://news.naver.com/main/list.naver" + x, other_pages))

    def extract_article_item(self, article_res: Response) -> NewsItem:
        title: str = article_res.css("head title::text").get()
        article_str: str = self.re_article_ptrn.search(article_res.text).group(1)
        article_dict: Dict = json.loads(self.js_object_to_json(article_str, ["document.title"]))
        office_str: str = self.re_office_ptrn.search(article_res.text).group(1)
        office_dict: Dict = json.loads(self.js_object_to_json(office_str))

        content: List[str] = self.strip_and_filter_str_list(article_res.css("div#dic_area::text").getall())
        content: str = self.join_char.join(content)
        # summary: str = article_res.css("div#dic_area strong.media_end_summary::text").get()
        sid1: str = article_dict["sectionInfo"]["firstSection"]
        sid2: str = article_dict["sectionInfo"]["secondSection"]
        sid3: str = article_dict["sectionInfo"]["thirdSection"]
        url: str = article_res.url.split("?")[0] if "?" in article_res.url else article_res.url
        upload_time: str = article_res.css("span._ARTICLE_DATE_TIME::attr(data-date-time)").get()
        edited_time: str = article_res.css("span._ARTICLE_MODIFY_DATE_TIME::attr(data-modify-date-time)").get()
        press: str = office_dict["name"]
        author: str = article_res.css(
            "button.media_end_head_journalist_btn_subscribe._UNSUBSCRIBE::attr(data-messagevalue)"
        ).get()

        item: NewsItem = NewsItem(
            oid=article_dict["officeId"],
            aid=article_dict["articleId"],
            title=title,
            content=content,
            sid1=sid1,
            sid2=sid2,
            sid3=sid3,
            url=url,
            upload_time=upload_time,
            edited_time=edited_time if edited_time else upload_time,
            press=press,
            author=author
        )
        self.logger.debug(f"Extracted item: {item}")
        return item

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        yield scrapy.Request(url=self.list_url.format(date=self.date, page=1), callback=self.parse_list)

    def parse_list(self, response: Response) -> Generator[scrapy.Request, None, None]:
        for page in self.extract_pages(response):
            yield Request(url=page, callback=self.parse_list)

        for link in self.extract_article_links(response):
            yield Request(url=link, callback=self.parse_article)

    def parse_article(self, response: Response) -> Generator[NewsItem, None, None]:
        yield self.extract_article_item(response)
