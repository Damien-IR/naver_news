import re
from abc import ABCMeta
from datetime import datetime
from typing import List, Dict, Generator, Union
from urllib.parse import urlparse, parse_qs

from scrapy import Spider, Selector, Request
from scrapy.http import Response

from src.items import News, Author
from src.utils import (
    get_now_dt_str,
    remove_query_and_fragment,
    js_object_to_json,
    get_oaid_from_news_url,
    strip_and_filter_str_list,
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

    def fmt_list_url(self, date: Union[str, datetime], page: int = 1) -> str:
        if isinstance(date, datetime):
            date = date.strftime("%Y%m%d")
        return self.list_url.format(date=date, page=page)

    def extract_article_item(self, article_res: Response) -> News:
        title: str = article_res.css("head title::text").get()
        article_str: str = self.re_article_ptrn.search(article_res.text).group(1)
        article_dict: Dict = js_object_to_json(article_str, ["document.title"])
        office_str: str = self.re_office_ptrn.search(article_res.text).group(1)
        office_dict: Dict = js_object_to_json(office_str)
        oid, aid = get_oaid_from_news_url(article_res.url)

        content: List[str] = strip_and_filter_str_list(
            article_res.css("div#dic_area::text").getall()
        )
        content: str = self.join_char.join(content)
        # summary: str = article_res.css("div#dic_area strong.media_end_summary::text").get()
        sid1: str = article_dict["sectionInfo"]["firstSection"]
        sid2: str = article_dict["sectionInfo"]["secondSection"]
        sid3: str = article_dict["sectionInfo"]["thirdSection"]
        url: str = remove_query_and_fragment(article_res.url)
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
        yield Request(url=self.fmt_list_url(date=self.date), callback=self.parse_list)

    def parse_list(self, response: Response) -> Generator[Request, None, None]:
        for page in self.extract_pages(response):
            yield Request(url=page, callback=self.parse_list)

        for link in self.extract_article_links(response):
            yield Request(url=link, callback=self.parse_article)

    def parse_article(self, response: Response) -> Generator[News, None, None]:
        yield self.extract_article_item(response)


class LSDSpider(NewsSpider, metaclass=ABCMeta):
    name: str = "LSDSpider"

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        sid: str = "100",
        **kwargs,
    ):
        super().__init__(date, join_char, **kwargs)
        self.list_url: str = (
            "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&listType=title"
            "&sid1={sid1}&date={date}&page={page}"
        )
        self.article_url: str = "https://n.news.naver.com/mnews/article/{oid}/{aid}"
        self.sid: str = sid

    def convert_url(self, url: str, conv: str = "mnews") -> str:
        if "mnews" in url and conv != "mnews":
            url: str = url.replace("mnews", conv)
        else:
            parsed_url: urlparse = urlparse(url)
            query_dict: Dict = parse_qs(parsed_url.query)
            oid: str = query_dict["oid"][0]
            aid: str = query_dict["aid"][0]
            url = self.article_url.format(oid=oid, aid=aid)
        return remove_query_and_fragment(url)

    def fmt_list_url(self, date: Union[str, datetime], page: int = 1) -> str:
        if isinstance(date, datetime):
            date = date.strftime("%Y%m%d")
        return self.list_url.format(sid1=self.sid, date=date, page=page)

    def extract_article_links(self, list_res: Response) -> List[str]:
        link_list: List[str] = super().extract_article_links(list_res)

        return list(map(self.convert_url, link_list))

    def start_requests(self) -> Generator[Request, None, None]:
        yield Request(
            url=self.fmt_list_url(self.date),
            callback=self.parse_list,
        )


class EntSpider(LSDSpider, metaclass=ABCMeta):
    name: str = "EntSpider"

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        sid: str = "106",
        **kwargs,
    ):
        super().__init__(date=date, join_char=join_char, sid=sid, **kwargs)
        self.article_url: str = "https://n.news.naver.com/entertain/article/{oid}/{aid}"

    def convert_url(self, url: str, conv: str = "entertain") -> str:
        return super().convert_url(url, conv)


class SportSpider(LSDSpider, metaclass=ABCMeta):
    name: str = "SportSpider"

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        sid: str = "107",
        **kwargs,
    ):
        super().__init__(date=date, join_char=join_char, sid=sid, **kwargs)
        self.article_url: str = "https://n.news.naver.com/sports/article/{oid}/{aid}"

    def convert_url(self, url: str, conv: str = "sports") -> str:
        return super().convert_url(url, conv)
