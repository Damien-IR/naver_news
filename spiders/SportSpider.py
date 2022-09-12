from abc import ABCMeta

from scrapy.http import Response


from items import News
from spiders.EntSpider import EntSpider
from utils import get_now_dt_str


class SportSpider(EntSpider, metaclass=ABCMeta):
    name: str = "SportSpider"

    def __init__(
        self,
        date: str = get_now_dt_str(),
        join_char: str = "\n",
        sid: str = "107",
        **kwargs
    ):
        super().__init__(date=date, join_char=join_char, sid=sid, **kwargs)

    def extract_article_item(self, article_res: Response) -> News:
        item: News = super().extract_article_item(article_res)
        item.url = "https://sports.news.naver.com/news?oid={oid}&aid={aid}".format(
            oid=item.oid, aid=item.aid
        )
        return item
