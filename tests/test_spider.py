import unittest
from typing import List

from scrapy.http import Response

from src.items import News
from src.spiders import NewsSpider, EntSpider, SportSpider
from src.utils import get_scrapy_res_from_url


class TestSpider(unittest.TestCase):
    def setUp(self) -> None:
        self.news_spider: NewsSpider = NewsSpider()
        self.ent_spider: EntSpider = EntSpider()
        self.sport_spider: SportSpider = SportSpider()

    def test_news_extract_list(self):
        list_res: Response = get_scrapy_res_from_url(
            self.news_spider.fmt_list_url(date="20210101")
        )
        self.assertEqual(list_res.status, 200)
        self.assertEqual(
            len(self.news_spider.extract_article_links(list_res)),
            50,
        )

    def test_news_extract_article1(self):
        article_res: Response = get_scrapy_res_from_url(
            "https://n.news.naver.com/mnews/article/015/0004476873"
        )
        news_item: News = self.news_spider.extract_article_item(article_res)
        self.assertEqual(article_res.status, 200)
        self.assertEqual(news_item.oid, "015")
        self.assertEqual(news_item.aid, "0004476873")
        self.assertEqual(news_item.sid1, "103")
        self.assertEqual(news_item.sid2, "321")
        self.assertEqual(news_item.sid3, "000")
        self.assertEqual(
            news_item.url, "https://n.news.naver.com/mnews/article/015/0004476873"
        )
        self.assertEqual(news_item.upload_time, "2021-01-01 23:59:39")
        self.assertEqual(news_item.edited_time, "2021-01-01 23:59:39")
        self.assertEqual(len(news_item.authors), 1)
        self.assertEqual(news_item.authors[0].oid, "015")
        self.assertEqual(news_item.authors[0].id, "74440")

    def test_news_extract_article2(self):
        article_res: Response = get_scrapy_res_from_url(
            "https://n.news.naver.com/mnews/article/015/0004476873"
        )
        news_item: News = self.news_spider.extract_article_item(article_res)
        self.assertEqual(article_res.status, 200)
        self.assertEqual(news_item.oid, "015")
        self.assertEqual(news_item.aid, "0004476873")
        self.assertEqual(news_item.sid1, "103")
        self.assertEqual(news_item.sid2, "321")
        self.assertEqual(news_item.sid3, "000")
        self.assertEqual(
            news_item.url, "https://n.news.naver.com/mnews/article/015/0004476873"
        )
        self.assertEqual(news_item.upload_time, "2021-01-01 23:59:39")
        self.assertEqual(news_item.edited_time, "2021-01-01 23:59:39")
        self.assertEqual(len(news_item.authors), 1)
        self.assertEqual(news_item.authors[0].oid, "015")
        self.assertEqual(news_item.authors[0].id, "74440")

    def test_news_extract_multi_authors(self):
        article_res: Response = get_scrapy_res_from_url(
            "https://n.news.naver.com/mnews/article/056/0010963679"
        )
        news_item: News = self.news_spider.extract_article_item(article_res)
        self.assertEqual(article_res.status, 200)
        self.assertEqual(news_item.oid, "056")
        self.assertEqual(news_item.aid, "0010963679")
        self.assertEqual(news_item.sid1, "100")
        self.assertEqual(news_item.sid2, "269")
        self.assertEqual(news_item.sid3, "000")
        self.assertEqual(
            news_item.url, "https://n.news.naver.com/mnews/article/056/0010963679"
        )
        self.assertEqual(news_item.upload_time, "2021-01-01 21:25:01")
        self.assertEqual(news_item.edited_time, "2021-01-01 22:19:26")
        self.assertEqual(len(news_item.authors), 2)
        self.assertEqual(news_item.authors[0].oid, "056")
        self.assertEqual(news_item.authors[0].id, "71060")
        self.assertEqual(news_item.authors[1].oid, "056")
        self.assertEqual(news_item.authors[1].id, "71477")

    def test_ent_news_extract_list(self):
        list_res: Response = get_scrapy_res_from_url(
            self.ent_spider.fmt_list_url(date="20210101", page=1)
        )
        self.assertEqual(list_res.status, 200)
        self.assertEqual(
            len(self.ent_spider.extract_article_links(list_res)),
            50,
        )
        self.assertEqual(
            len(
                list(
                    filter(
                        lambda x: "mnews" not in x and "entertain" in x,
                        self.ent_spider.extract_article_links(list_res),
                    )
                )
            ),
            50,
        )

    def test_ent_news_extract_article(self):
        list_res: Response = get_scrapy_res_from_url(
            self.ent_spider.fmt_list_url(date="20210101", page=1)
        )
        list_links: List[str] = self.ent_spider.extract_article_links(list_res)
        news_item: News = self.ent_spider.extract_article_item(
            get_scrapy_res_from_url(list_links[0])
        )
        self.assertEqual(list_res.status, 200)
        self.assertEqual(news_item.oid, "108")
        self.assertEqual(news_item.aid, "0002921996")
        self.assertEqual(news_item.sid1, "106")
        self.assertEqual(news_item.sid2, "224")
        self.assertEqual(news_item.sid3, "000")
        self.assertEqual(
            news_item.url, "https://n.news.naver.com/entertain/article/108/0002921996"
        )
        self.assertEqual(news_item.upload_time, "2021-01-01 23:57:47")
        self.assertEqual(news_item.edited_time, "2021-01-01 23:58:37")
        self.assertEqual(len(news_item.authors), 1)
        self.assertEqual(news_item.authors[0].oid, "108")
        self.assertEqual(news_item.authors[0].id, "44044")

    def test_sport_news_extract_list(self):
        list_res: Response = get_scrapy_res_from_url(
            self.sport_spider.fmt_list_url(date="20210101")
        )
        list_links: List[str] = self.sport_spider.extract_article_links(list_res)
        self.assertEqual(list_res.status, 200)
        self.assertEqual(
            len(list_links),
            50,
        )
        self.assertEqual(
            len(list(filter(lambda x: "mnews" not in x and "sports" in x, list_links))),
            50,
        )

    def test_sport_news_extract_article(self):
        list_res: Response = get_scrapy_res_from_url(
            self.sport_spider.fmt_list_url(date="20210101")
        )
        list_links: List[str] = self.sport_spider.extract_article_links(list_res)
        news_item: News = self.sport_spider.extract_article_item(
            get_scrapy_res_from_url(list_links[0])
        )
        self.assertEqual(list_res.status, 200)
        self.assertEqual(news_item.oid, "139")
        self.assertEqual(news_item.aid, "0002144438")
        self.assertEqual(news_item.sid1, "107")
        self.assertEqual(news_item.sid2, "77a")
        self.assertEqual(news_item.sid3, "77b")
        self.assertEqual(
            news_item.url, "https://n.news.naver.com/sports/article/139/0002144438"
        )
        self.assertEqual(news_item.upload_time, "2021-01-01 23:58:42")
        self.assertEqual(news_item.edited_time, "2021-01-01 23:58:42")
        self.assertEqual(len(news_item.authors), 1)
        self.assertEqual(news_item.authors[0].oid, "139")
        self.assertEqual(news_item.authors[0].id, "43052")
