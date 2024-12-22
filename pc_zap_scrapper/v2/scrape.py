import re
import asyncio
import random
import uuid
from importlib import resources
from time import sleep
from datetime import datetime
from typing import get_args
from tqdm.asyncio import tqdm_asyncio
from urllib.request import Request, urlopen
from urllib.error import HTTPError


import backoff
import pandas as pd
from loguru import logger
from bs4 import BeautifulSoup
from unidecode import unidecode
from random_user_agent.user_agent import UserAgent
from playwright.async_api import async_playwright

from pc_zap_scrapper.v2.models import RealEstateInfo, ZapImoveisURL
from pc_zap_scrapper.v2.config import config, REAL_ESTATE_TYPES, ACTION_TYPES
from pc_zap_scrapper.v2.utils import get_integer_fields, suppress_errors_and_log


def backoff_hdlr(details):
    sleep(3)
    logger.warning(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=3,
    logger=logger,
    on_backoff=backoff_hdlr,
)
async def get_estates_from_page(
    action: ACTION_TYPES,
    type: REAL_ESTATE_TYPES,
    localization: str,
    page: int,
    max_estates_per_page: int | None = None,
    expected_estates_per_page: int | None = None,
    max_scroll_iter_per_page: int | None = None,
):
    if action != "venda":
        raise NotImplementedError(
            f"Action '{action}' not implemented yet. Available actions are: {list(get_args(ACTION_TYPES))}"
        )

    divs = await scrape_estate_divs_from_page(
        action=action,
        type=type,
        localization=localization,
        page=page,
        max_estates_per_page=max_estates_per_page,
        expected_estates_per_page=expected_estates_per_page,
        max_scroll_iter_per_page=max_scroll_iter_per_page,
    )

    search_date = datetime.now()
    estate_info = [get_info_from_div(div, action, search_date).model_dump() for div in divs]
    estates = pd.DataFrame(estate_info)

    integer_columns = get_integer_fields(RealEstateInfo)

    for col in integer_columns:
        estates[col] = estates[col].astype("Int64")

    estates = estates.where(pd.notnull(estates), None)

    return estates


def get_info_from_div(div, action: ACTION_TYPES, search_date: str | None = None):

    def _format_neighbor_name(text: str) -> str:
        if text:
            return unidecode(text.strip().lower())
        return None

    pc_neighbors_latlong = (
        pd.read_parquet(resources.files("pc_zap_scrapper").joinpath("datasets/external/neighbor_latlong.parquet"))
        .set_index("neighborhood")
        .to_dict(orient="index")
    )

    pc_neighbors_latlong = {_format_neighbor_name(k): v for k, v in pc_neighbors_latlong.items() if k}

    search_date = search_date or datetime.now()
    prices = _get_prices(div)
    snippet = _get_snippet(div)
    location = _get_location(div)
    type = _get_type(div)
    neighbor = location.get("neighbor")
    formatted_neighbor_name = _format_neighbor_name(neighbor)
    latlong = pc_neighbors_latlong.get(formatted_neighbor_name, {}) if formatted_neighbor_name else {}
    latitude = latlong.get("latitude", None)
    longitude = latlong.get("longitude", None)

    return RealEstateInfo(
        estate_id=_get_id(div),
        action=action,
        search_date=search_date,
        post_type=_get_post_type(div),
        link=_get_link(div),
        type=type,
        image_list=_get_image_list(div),
        snippet=snippet,
        street=location.get("street"),
        neighbor=neighbor,
        city=location.get("city"),
        state=location.get("state"),
        latitude=latitude,
        longitude=longitude,
        floor_size=_get_floor_size(div),
        number_of_rooms=_get_number_of_rooms(div),
        number_of_bathrooms=_get_number_of_bathrooms(div),
        number_of_parking_spaces=_get_parking_spaces_quantity(div),
        amenities_list=_get_amenities_list(div),
        price=prices.get("price"),
        condominium=prices.get("condominium"),
        iptu=prices.get("iptu"),
    )


async def scrape_estate_divs_from_page(
    action: ACTION_TYPES,
    type: REAL_ESTATE_TYPES,
    localization: str,
    page: int,
    max_estates_per_page: int | None = None,
    expected_estates_per_page: int | None = None,
    max_scroll_iter_per_page: int | None = None,
):

    max_estates_per_page = max_estates_per_page or config.MAX_ESTATES_PER_PAGE
    max_scroll_iter_per_page = max_scroll_iter_per_page or config.MAX_SCROLL_ITER_PER_PAGE
    expected_estates_per_page = expected_estates_per_page or max_estates_per_page or config.EXPECTED_ESTATES_PER_PAGE

    url = ZapImoveisURL(action=action, type=type, localization=localization, page=page)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=UserAgent().get_random_user_agent(),
        )
        context.set_default_timeout(config.BROWSER_TIMEOUT)

        page = await context.new_page()

        await page.set_extra_http_headers(config.BROWSER_EXTRA_HTTP_HEADERS)
        await page.goto(url.text)

        n_pages = 0
        count = 1
        divs = None
        with tqdm_asyncio(total=expected_estates_per_page, desc="Inicializando") as pbar:
            while n_pages < max_estates_per_page and count <= max_scroll_iter_per_page:
                await _perform_user_actions(page)
                divs = await _scroll_and_get_divs(page)
                n_new_divs = len(divs)

                pbar.set_description(f"Loop {count} | {n_new_divs} elementos")
                pbar.update(n_new_divs - n_pages)

                if n_pages == n_new_divs:
                    pbar.n = n_new_divs
                    pbar.total = n_new_divs
                    pbar.refresh()
                    break

                n_pages = n_new_divs
                count += 1

            return divs


@suppress_errors_and_log
def _get_post_type(div):
    return div.get("data-type", None)


@suppress_errors_and_log
def _get_id(div):
    if link := div.find("a"):
        return link.get("data-id", None)
    return str(uuid.uuid4())[:10]


@suppress_errors_and_log
def _get_link(div):
    if link := div.find("a"):
        return link.get("href", None)


@suppress_errors_and_log
def get_estate_type(div):
    if link := div.find("a"):
        return link.get("itemtype", None)


@suppress_errors_and_log
def _get_image_list(div):
    return [x.get("src", None) for x in div.findAll("img", class_="l-image") if x.get("src", None)]


@suppress_errors_and_log
def _get_snippet(div):
    if subtitle := div.find("h2", attrs={"data-testid": "card-header"}):
        if spans := subtitle.findAll("span"):
            texts = [x.text for x in spans]
            return texts[0].split(",")[0]

    if subtitle := div.find("h2"):
        return subtitle.text


@suppress_errors_and_log
def _get_location(div):
    if subtitle := div.find("h2", attrs={"data-testid": "card-header"}):
        if spans := subtitle.findAll("span"):
            texts = [x.text for x in spans]
            *street, neighbor, city, state = [x.strip() for x in texts[1].replace("-", ",").split(",")]
            return {
                "street": " - ".join(street),
                "neighbor": neighbor,
                "city": city,
                "state": state,
            }

    if subtitle := div.find("h2"):
        elements = str(subtitle.text).split(",")
        if len(elements) == 2:
            return {
                "street": None,
                "neighbor": elements[0],
                "city": elements[1],
                "state": None,
            }
        logger.warning(f"It wa not possible to get locatino info from snippet '{subtitle}'")
    return {
        "street": None,
        "neighbor": None,
        "city": None,
        "state": None,
    }


@suppress_errors_and_log
def get_amenity(div, itemprop):
    section = div.find("section", class_=re.compile(r"card-amenities"))
    amenities_paragraph = section.find("p", attrs=dict(itemprop=itemprop))
    if amenities_paragraph:
        return amenities_paragraph.text


def format_property_numbers(value):
    if not value:
        return
    value = value.replace("m²", "").strip()
    if "-" in value:
        return int(value.split("-")[0])
    return int(value)


@suppress_errors_and_log
def _get_floor_size(div):
    floor_size = get_amenity(div, "floorSize")
    return format_property_numbers(floor_size)


@suppress_errors_and_log
def _get_number_of_rooms(div):
    number_of_rooms = get_amenity(div, "numberOfRooms")
    if number_of_rooms:
        return format_property_numbers(number_of_rooms)


@suppress_errors_and_log
def _get_number_of_bathrooms(div):
    number_of_bathrooms = get_amenity(div, "numberOfBathroomsTotal")
    if number_of_bathrooms:
        return format_property_numbers(number_of_bathrooms)


@suppress_errors_and_log
def _get_parking_spaces_quantity(div):
    section = div.find("section", class_=re.compile(r"card-amenities"))
    if parking_spaces_paragrah := section.find("p", attrs={"data-cy": re.compile(r"parkingSpacesQuantity")}):
        return format_property_numbers(parking_spaces_paragrah.text)


@suppress_errors_and_log
def _get_amenities_list(div):
    amenities_list = div.find("ul", attrs={"aria-label": "Lista de amenidades"})
    if amenities_list:
        return [x.text for x in amenities_list.findAll("li") if "..." not in x.text]


@suppress_errors_and_log
def _get_prices(div):
    def get_estate_price(value: str):
        match = re.search(r"R\$\s*([\d.]+)", value)
        if match:
            return float(match.group(1).replace(".", ""))
        return None

    def get_cond_and_tax(input_string):
        pattern = r"([\w\.]+)\s*R\$\s*(\d+)"
        matches = re.findall(pattern, input_string)
        return {key: int(value) for key, value in matches}

    prices_container = div.find("div", attrs={"data-cy": re.compile(r"cardProperty-price")})
    textual_prices = prices_container.findAll("p")

    response = {
        "price": get_estate_price(textual_prices[0].text),
    }

    if len(textual_prices) > 1:
        cond_and_tax = get_cond_and_tax(textual_prices[1].text)
        response["condominium"] = cond_and_tax.get("Cond.")
        response["iptu"] = cond_and_tax.get("IPTU")

    return response


@suppress_errors_and_log
def _get_type(div):

    if snippet := _get_snippet(div):
        type = _get_type_from_snippet(snippet)

    if type:
        return type

    if "apartamento" in str(div).lower():
        return "Apartamento"

    if "casa" in str(div).lower():
        return "Casa"

    if "cobertura" in str(div).lower():
        return "Apartamento"

    if "flat" in str(div).lower():
        return "Flat"

    if "chacara" in unidecode(str(div).lower()):
        return "Rural"

    if "sitio" in unidecode(str(div).lower()):
        return "Rural"

    if "fazenda" in unidecode(str(div).lower()):
        return "Rural"


@suppress_errors_and_log
def _get_type_from_snippet(snippet):
    if not snippet:
        logger.warning("No snippet found")
        return None
    snippet = str(snippet)
    is_rural = ("fazenda" in snippet.lower()) or ("sítio" in snippet.lower()) or ("chácara" in snippet.lower())
    is_comercial = ("ponto comercial" in snippet.lower()) or ("loja" in snippet.lower()) or ("box" in snippet.lower())
    is_lote = ("lote" in snippet.lower()) or ("terreno" in snippet.lower())

    if "apartamento" in snippet.lower():
        return "Apartamento"

    if "casa" in snippet.lower():
        return "Casa"

    if is_lote:
        return "Lote"

    if "flat" in snippet.lower():
        return "Flat"

    if "cobertura" in snippet.lower():
        return "Apartamento"

    if is_comercial:
        return "Comercial"

    if is_rural:
        return "Rural"


async def _random_delay(min_delay=1, max_delay=3):
    await asyncio.sleep(random.uniform(min_delay, max_delay))


async def _simulate_user_actions(page):
    for _ in range(random.randint(3, 7)):
        x, y = random.randint(0, 800), random.randint(0, 600)
        await page.mouse.move(x, y)
        await _random_delay(0.1, 0.5)


async def _scroll_position(page):
    await page.wait_for_selector("[data-position]")
    await page.evaluate(
        """
        () => {
            const elements = document.querySelectorAll('[data-position]');
            if (elements.length > 0) {
                elements[elements.length - 1].scrollIntoView();
            }
        }
    """
    )
    await _simulate_user_actions(page)
    await _random_delay(3, 5)


async def _fetch_page_content(page):
    html_page = await page.content()
    return BeautifulSoup(html_page, "html.parser")


async def _perform_user_actions(page):
    await _simulate_user_actions(page)
    await _random_delay(1, 3)


async def _scroll_and_get_divs(page):
    await _scroll_position(page)
    soup = await _fetch_page_content(page)
    return soup.find_all("div", attrs={"data-position": True})


@backoff.on_exception(
    backoff.expo,
    HTTPError,
    max_tries=3,
    logger=logger,
    on_backoff=backoff_hdlr,
)
def get_html_page(url):

    logger.debug(f"Requesting info from '{url}'")

    request = Request(url)
    user_agent = UserAgent().get_random_user_agent()
    request.add_header("User-Agent", user_agent)
    try:
        html_page = urlopen(request, timeout=20)
    except HTTPError as e:
        logger.error("[error]", e)
        raise e

    return BeautifulSoup(html_page, "html.parser")


def get_number_of_real_estates(soup_object: BeautifulSoup):
    title_element = soup_object.find("div", {"class": "result-wrapper__title"})
    return int(re.sub("[^0-9]", "", title_element.text))


def get_number_of_pages(number_of_real_estates: int):
    return number_of_real_estates // 100 if number_of_real_estates // 100 > 1 else 1
