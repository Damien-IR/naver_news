from abc import ABCMeta
from typing import Generator

import scrapy

from spiders.EntSpider import EntSpider


class SportSpider(EntSpider, metaclass=ABCMeta):
    name = 'SportSpider'

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        yield scrapy.Request(url=self.list_url.format(sid1="107", date=self.date, page=1), callback=self.parse_list)
