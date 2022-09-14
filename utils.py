import json
import re
from datetime import datetime
from typing import Optional, Dict, List, Iterable, Callable, Tuple
from urllib.parse import urlsplit, urlunsplit, urlparse, ParseResult

import requests
from scrapy.http import HtmlResponse

from settings import USER_AGENT


def remove_query_and_fragment(url: str) -> str:
    return urlunsplit(urlsplit(url)._replace(query="", fragment=""))


def get_oaid_from_news_url(url: str) -> Tuple[str, str]:
    url_split: ParseResult = urlparse(url)
    path_split: List[str] = url_split.path.split("/")
    oid: str = path_split[-2]
    aid: str = path_split[-1]
    return oid, aid


def strptime_util(
    datetime_str: str,
    fmt: str = "%Y.%m.%d. %p %I:%M",
    replace_dict: Optional[Dict] = None,
) -> datetime:
    if not replace_dict:
        replace_dict: Dict = {"오전": "AM", "오후": "PM"}
    for key, value in replace_dict.items():
        datetime_str = datetime_str.replace(key, value)
    return datetime.strptime(datetime_str, fmt)


def strftime_util(datetime_obj: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime_obj.strftime(fmt)


def get_now_dt() -> datetime:
    return datetime.now()


def get_now_dt_str(fmt: str = "%Y%m%d") -> str:
    return get_now_dt().strftime(fmt)


def strip_and_filter_str_list(
    str_list: List[str], func: Callable = lambda x: x != ""
) -> List[str]:
    return list(filter(func, map(lambda x: x.strip(), str_list)))


def js_object_to_json(
    js_object: str, remove_str_iter: Optional[Iterable[str]] = None
) -> Dict:
    result: str = re.sub(r"(\w+)\s*:", r'"\1":', js_object)
    if remove_str_iter:
        for string in remove_str_iter:
            result = result.replace(string, '""')
    return json.loads(result)


def convert_requests_res_to_scrapy(res: requests.Response) -> HtmlResponse:
    # convert requests.Response to scrapy.Response
    return HtmlResponse(
        url=res.url,
        status=res.status_code,
        headers=res.headers,
        body=res.content.decode(res.encoding),
        request=res.request,
        encoding=res.encoding,
    )


def get_scrapy_res_from_url(url: str, params=None, **kwargs) -> HtmlResponse:
    try:
        if not kwargs["headers"]["User-Agent"]:
            kwargs["headers"]["User-Agent"] = USER_AGENT
    except KeyError:
        kwargs["headers"] = {"User-Agent": USER_AGENT}
    res: requests.Response = requests.get(url, params, **kwargs)
    return convert_requests_res_to_scrapy(res)
