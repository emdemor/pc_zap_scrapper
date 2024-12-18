import asyncio
import backoff
import os
import sys
from urllib.parse import quote_plus
from loguru import logger
import typer
from pc_zap_scrapper import __version__
from pc_zap_scrapper import (
    DEFAULT_ACTION,
    DEFAULT_LOCALIZATION,
    DEFAULT_TYPE,
    DatabaseHandler,
    TableRealEstateInfo,
)
from pc_zap_scrapper.v2.scrape import (
    get_estates_from_page,
    get_html_page,
    get_number_of_pages,
    get_number_of_real_estates,
)

app = typer.Typer(help="Command line interface for zap scrapping")


@app.command()
def scrape(
    action: str = typer.Option(
        DEFAULT_ACTION,
        "-a",
        "--action",
        help="Action to find. Can be 'venda' or 'aluguel'",
    ),
    estate_type: str = typer.Option(
        DEFAULT_TYPE,
        "-t",
        "--estate-type",
        help="Estate type. Can be 'imoveis', 'casas' ou 'apartamentos'",
    ),
    location: str = typer.Option(
        DEFAULT_LOCALIZATION,
        "-l",
        "--location",
        help="City and state, in the format 'uf+city-name'",
    ),
    max_pages: int = typer.Option(
        None,
        "-m",
        "--max-pages",
        help="Max number of pages",
    ),
):
    """
    Run the scrapper for defined action, estate_type, and location.
    """
    asyncio.run(scrape_async(action, estate_type, location, max_pages))


async def scrape_async(action: str, estate_type: str, location: str, max_pages: int):
    """
    Function to execute the scraping asynchronously.
    """
    logger.info(f"Scraping with action={action}, estate_type={estate_type}, location={location}, max_pages={max_pages}")

    # Configuração do banco de dados
    db_params = dict(
        user=os.getenv("PSQL_USERNAME"),
        password=quote_plus(os.getenv("PSQL_PASSWORD")),
        host=os.getenv("PSQL_HOST"),
        port=os.getenv("PSQL_PORT"),
        dbname=os.getenv("PSQL_NAME"),
    )

    db_handler = DatabaseHandler(db_params, table=TableRealEstateInfo, echo=False)

    try:
        soup = get_html_page(f"https://www.zapimoveis.com.br/{action}/{estate_type}/{location}")
        number_of_real_estates = get_number_of_real_estates(soup)
        number_of_pages = get_number_of_pages(number_of_real_estates)
        logger.info(f"number_of_real_estates = {number_of_real_estates}")
        logger.info(f"number_of_pages = {number_of_pages}")

        N_EXPECTED_PAGES = max_pages or 25

        for page in range(1, min(number_of_pages + 1, N_EXPECTED_PAGES + 1)):
            try:
                await _scrape_page(page, action, estate_type, location, db_handler)
            except PageScrapeError as e:
                logger.error(f"Erro ao processar página {page}: {e}")
                continue

    finally:
        await db_handler.close()
        logger.info("Database handler closed.")

class PageScrapeError(Exception):
    pass

def backoff_hdlr(details):
    print ("Backing off {wait:0.1f} seconds after {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))

@backoff.on_exception(backoff.expo, PageScrapeError, max_tries=3, on_backoff=backoff_hdlr)
async def _scrape_page(page, action, estate_type, location, db_handler):
    logger.info(f"Scraping page {page}")
    try:

        estates = await get_estates_from_page(
            action=action,
            type=estate_type,
            localization=location,
            page=page,
        )

        await db_handler.create_table()
        await db_handler.insert_data(estates)
    except Exception as e:
        message = f"Erro ao persistir dados da página {page}."
        logger.warning(message + " Uma nova tentativa será realizada.")
        raise PageScrapeError(message)

@app.command()
def version():
    """
    Print the version of the application.
    """
    sys.stdout.write(f"{__version__}\n")


def main():
    app()


if __name__ == "__main__":
    main()
