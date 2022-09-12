import json
import re
from abc import ABCMeta
from typing import Generator, List, Dict

from scrapy import Selector
from scrapy.http import Request, Response
from scrapy.spiders import Spider

from items import News, Author
from utils import (
    js_object_to_json,
    strip_and_filter_str_list,
    get_oaid_from_news_url,
    get_now_dt_str,
)


class NewsSpider(Spider, metaclass=ABCMeta):
    name: str = "NewsSpider"
    allowed_domains: List[str] = ["naver.com"]

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.date: str = date
        self.join_char: str = join_char
        self.list_url: str = (
            "https://news.naver.com/main/list.naver?mode=LS2D&mid=sec&listType=title&"
            "date={date}&page={page}"
        )
        self.author_url: str = (
            "https://media.naver.com/journalist/{office_id}/{author_id}"
        )

        self.re_article_ptrn: re.Pattern = re.compile(r"var article = (\{[^;]+});")
        self.re_office_ptrn: re.Pattern = re.compile(r"var office = (\{[^;]+});")

    @staticmethod
    def extract_article_links(list_res: Response) -> List[str]:
        return list_res.css("div.list_body ul.type02 li a::attr(href)").getall()

    @staticmethod
    def extract_pages(list_res: Response) -> List[str]:
        other_pages: List[str] = list_res.css("div.paging a::attr(href)").getall()
        return list(
            map(lambda x: "https://news.naver.com/main/list.naver" + x, other_pages)
        )

    def extract_article_item(self, article_res: Response) -> News:
        title: str = article_res.css("head title::text").get()
        article_str: str = self.re_article_ptrn.search(article_res.text).group(1)
        article_dict: Dict = json.loads(
            js_object_to_json(article_str, ["document.title"])
        )
        office_str: str = self.re_office_ptrn.search(article_res.text).group(1)
        office_dict: Dict = json.loads(js_object_to_json(office_str))

        oid, aid = get_oaid_from_news_url(article_res.url)

        content: List[str] = strip_and_filter_str_list(
            article_res.css("div#dic_area::text").getall()
        )
        content: str = self.join_char.join(content)
        # summary: str = article_res.css("div#dic_area strong.media_end_summary::text").get()
        sid1: str = article_dict["sectionInfo"]["firstSection"]
        sid2: str = article_dict["sectionInfo"]["secondSection"]
        sid3: str = article_dict["sectionInfo"]["thirdSection"]
        url: str = article_res.url.split("?")[0].split("#")[0]
        upload_time: str = article_res.css(
            "span._ARTICLE_DATE_TIME::attr(data-date-time)"
        ).get()
        edited_time: str = article_res.css(
            "span._ARTICLE_MODIFY_DATE_TIME::attr(data-modify-date-time)"
        ).get()
        press: str = office_dict["name"]
        authors: List[Author] = self.extract_author_item(article_res)

        item: News = News(
            oid=oid,
            aid=aid,
            title=title,
            content=content,
            sid1=sid1,
            sid2=sid2,
            sid3=sid3,
            url=url,
            upload_time=upload_time,
            edited_time=edited_time if edited_time else upload_time,
            press=press,
            authors=authors,
        )
        return item

    def extract_author_item(self, article_res: Response) -> List[Author]:
        oid, aid = get_oaid_from_news_url(article_res.url)
        author_selector_list: List[Selector] = article_res.css(
            "button.media_end_head_journalist_btn_subscribe._UNSUBSCRIBE"
        )
        author_list: List[Author] = []
        for author in author_selector_list:
            author_id: str = author.css("::attr(data-channelkey)").get().split("_")[1]
            author_name: str = author.css("::attr(data-messagevalue)").get()
            author_url: str = self.author_url.format(office_id=oid, author_id=author_id)
            author_item: Author = Author(
                id=author_id,
                name=author_name,
                oid=oid,
                url=author_url,
            )
            author_list.append(author_item)

        return author_list

    def start_requests(self) -> Generator[Request, None, None]:
        yield Request(
            url=self.list_url.format(date=self.date, page=1), callback=self.parse_list
        )

    def parse_list(self, response: Response) -> Generator[Request, None, None]:
        for page in self.extract_pages(response):
            yield Request(url=page, callback=self.parse_list)

        for link in self.extract_article_links(response):
            yield Request(url=link, callback=self.parse_article)

    def parse_article(self, response: Response) -> Generator[News, None, None]:
        yield self.extract_article_item(response)
