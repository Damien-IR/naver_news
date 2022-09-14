import unittest
from datetime import datetime

from utils import (
    remove_query_and_fragment,
    get_oaid_from_news_url,
    strptime_util,
    strftime_util,
    strip_and_filter_str_list,
    js_object_to_json,
)


class TestUtils(unittest.TestCase):
    def test_remove_query_and_fragment(self):
        self.assertEqual(
            remove_query_and_fragment(
                "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&listType=title&date=20210101&page=1"
            ),
            "https://news.naver.com/main/list.naver",
        )

    def test_get_oaid_from_news_url(self):
        self.assertEqual(
            get_oaid_from_news_url(
                "https://n.news.naver.com/mnews/article/015/0004476873"
            ),
            ("015", "0004476873"),
        )
        self.assertEqual(
            get_oaid_from_news_url(
                "https://n.news.naver.com/mnews/article/014/0004557309",
            ),
            ("014", "0004557309"),
        )

    def test_strptime_util(self):
        self.assertEqual(
            strptime_util("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
            datetime(2021, 1, 1, 0, 0, 0),
        )
        self.assertEqual(
            strptime_util("2021.01.01. 오전 6:59", "%Y.%m.%d. %p %I:%M"),
            datetime(2021, 1, 1, 6, 59),
        )

    def test_strftime_util(self):
        self.assertEqual(
            strftime_util(datetime(2021, 1, 1, 0, 0, 0), "%Y-%m-%d %H:%M:%S"),
            "2021-01-01 00:00:00",
        )
        self.assertEqual(
            strftime_util(datetime(2021, 1, 1, 6, 59), "%Y.%m.%d. %p %I:%M"),
            "2021.01.01. AM 06:59",
        )

    def test_strip_and_filter_str_list(self):
        self.assertEqual(
            strip_and_filter_str_list(["  abc ", "def", "  ", "ghi  "]),
            ["abc", "def", "ghi"],
        )

    def test_json_object_to_json(self):
        self.assertEqual(
            js_object_to_json(
                js_object=(
                    "{\n"
                    "				    isSubscribe: false,\n"
                    '				    officeId: "015",\n'
                    '				    articleId: "0004476873",\n'
                    '				    sectionId : "103",\n'
                    '				    gdid: "88000107_000000000000000004476873",\n'
                    '				    type: "1",\n'
                    "				    sectionInfo: {\n"
                    '					    firstSection: "103",\n'
                    '				    	secondSection: "321",\n'
                    '			    		thirdSection: "000"\n'
                    "			    	},\n"
                    "                        title: document.title\n"
                    "			    }\n"
                ),
                remove_str_iter=["document.title"],
            ),
            {
                "isSubscribe": False,
                "officeId": "015",
                "articleId": "0004476873",
                "sectionId": "103",
                "gdid": "88000107_000000000000000004476873",
                "type": "1",
                "sectionInfo": {
                    "firstSection": "103",
                    "secondSection": "321",
                    "thirdSection": "000",
                },
                "title": "",
            },
        )
