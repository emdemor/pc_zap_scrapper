from loguru import logger
import warnings
from zapscrapper import zap_imoveis as zap

from pc_zap_scrapper import ACTION, PATH_DATA_RAW, LOCALIZATION, TYPE

warnings.filterwarnings("ignore")


def search_estates(action: str, type: str, localization: str, max_pages: int) -> None:
    """Search for estate for specifieds action, type and localization.

    :param action: Action related to estate. ('venda', 'aluguel')
    :type action: str
    :param type: Type of estate. ('casas', 'apartamentos')
    :type type: str
    :param localization: State and city
    :type localization: str
    :param max_pages: Max pages on scrapping
    :type max_pages: int
    """

    n_cases = zap.get_total(action, type, localization)

    final_page = int(n_cases / 24) + 1

    page_list = list(range(1, final_page + 1))

    if max_pages is not None:
        page_list = page_list[:int(max_pages)]

    logger.info("Scrapping data")
    df = zap.search(
        page_list,
        localization=localization,
        action=action,
        type=type,
        sleep_time_bias=10,
        sleep_time_mean=10,
        sleep_time_std=5,
        timeout=60,
    )

    logger.info(f"Persist to {PATH_DATA_RAW}")

    df.to_parquet(PATH_DATA_RAW)


if __name__ == "__main__":

    search_estates(ACTION, TYPE, LOCALIZATION)
