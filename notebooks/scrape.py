import time
from dataclasses import dataclass
from typing import List, Optional, Any

import backoff
from loguru import logger

import json
from http import HTTPStatus
from typing import List, Optional, Any
from pydantic import BaseModel

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from models import *


@dataclass
class RequestedPageResponse:
    html: Any
    code: int = 200
    exception: Exception | None = None

def get_page(url: str, timeout: int = 20, verbose: int = 0):

    request = Request(url)

    request.add_header("User-Agent", USER_AGENT)

    try:
        return RequestedPageResponse(html=urlopen(request, timeout=timeout))
    except HTTPError as e:
        logger.error("[error]", e)
        return RequestedPageResponse(html=None, code=e.getcode(), exception=e)



def backoff_hdlr(details):
    time.sleep(3)
    logger.warning("Backing off {wait:0.1f} seconds after {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))
    
@backoff.on_exception(
    backoff.expo,
    HTTPError,
    max_tries=3,
    logger=logger,
    on_backoff=backoff_hdlr,
)
def get_page_html(page, action, type, localization):
    url = f"https://www.zapimoveis.com.br/{action}/{type}/{localization}/?pagina={page}"
    logger.debug(f"Requesting info from '{url}'")

    response = get_page(url)

    if response.code != HTTPStatus.OK:
        raise response.exception

    return response.html

def get_real_state_data(page_html):
    soup = BeautifulSoup(page_html, "html.parser")
    script = soup.find('script', id='__NEXT_DATA__')
    listings = json.loads(script.text)
    raw_data = (
        listings
        .get("props", {})
        .get("pageProps", {})
        .get("initialProps", {})
        .get("data", {})
    )
    return [RealEstateElement(**d) for d in raw_data]
