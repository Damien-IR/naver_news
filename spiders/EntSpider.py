from abc import ABCMeta
from typing import List, Dict
from urllib.parse import parse_qs, urlparse

from scrapy.http import Response

from spiders.LSDSpider import LSDSpider
from utils import remove_query_and_fragment, get_now_dt_str


class EntSpider(LSDSpider, metaclass=ABCMeta):
    name: str = "EntSpider"

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        sid: str = "106",
        **kwargs
    ):
        super().__init__(date=date, join_char=join_char, sid=sid, **kwargs)
        self.article_url: str = "https://n.news.naver.com/entertain/article/{oid}/{aid}"

    def extract_article_links(self, list_res: Response) -> List[str]:
        link_list: List[str] = super().extract_article_links(list_res)

        def convert_url(url: str) -> str:
            if "oid" not in url or "aid" not in url:
                if "mnews" in url:
                    url: str = url.replace("mnews", "entertain")
                    return remove_query_and_fragment(url)
            else:
                parsed_url: urlparse = urlparse(url)
                query_dict: Dict = parse_qs(parsed_url.query)
                oid: str = query_dict["oid"][0]
                aid: str = query_dict["aid"][0]
                return self.article_url.format(oid=oid, aid=aid)

        return list(map(convert_url, link_list))
