import sys
import click
from loguru import logger
from dotenv import load_dotenv
from click_default_group import DefaultGroup

from pc_zap_scrapper import ACTION, LOCALIZATION, TYPE, PATH_TEMP_DOTENV, __version__
from pc_zap_scrapper.load import load
from pc_zap_scrapper.scrap import search_estates
from pc_zap_scrapper.transform import format_data
from pc_zap_scrapper.utils import set_directories, validate_environment, configure


@click.group(cls=DefaultGroup, default="main", default_if_no_args=True)
def cli():
    """Command line interface for zap scrapping"""
    pass


@cli.command(name="env")
def env():
    """Check environment variables"""

    if not load_dotenv(dotenv_path=PATH_TEMP_DOTENV):
        error_message = "No '.env' file was found."
        logger.error(error_message)
        raise Exception(error_message)

    validate_environment()


@cli.command(name="search")
@click.option(
    "-a",
    "--action",
    default=ACTION,
    help="Action to find. Can be 'venda' or 'aluguel'",
    type=str,
)
@click.option(
    "-t",
    "--estate_type",
    default=TYPE,
    help="Estate type. Can be 'imoveis', 'casas' ou 'apartamentos'",
    type=str,
)
@click.option(
    "-l",
    "--location",
    default=LOCALIZATION,
    help="City and state, in the format 'uf+city-name'",
    type=str,
)
@click.option(
    "-m",
    "--max_pages",
    default=None,
    help="Max number of pages",
    type=int,
)
def search(action: str, estate_type: str, location: str, max_pages: int):
    """Run the scrapper for defined action, estate_type and location"""
    logger.info("--> Search Function")
    search_estates(action, estate_type, location, max_pages)


@cli.command(name="format-data")
def format():
    logger.info("--> Format Data Function")
    format_data()


@cli.command(name="db-ingest")
def db_ingest():
    logger.info("--> DB Ingest Function")
    load()


@cli.command(name="configure")
@click.option(
    "-p",
    "--dotenv_path",
    default=None,
    help="Path to the .env file",
    type=str,
)
def config(dotenv_path):
    print("--> Config")
    configure(dotenv_path)

@cli.command(name="--version")
def version():
    sys.stdout.write(__version__)
    sys.stdout.write("\n")

@cli.command()
@click.option(
    "-a",
    "--action",
    default=ACTION,
    help="Action to find. Can be 'venda' or 'aluguel'",
    type=str,
)
@click.option(
    "-t",
    "--estate_type",
    default=TYPE,
    help="Estate type. Can be 'imoveis', 'casas' ou 'apartamentos'",
    type=str,
)
@click.option(
    "-l",
    "--location",
    default=LOCALIZATION,
    help="City and state, in the format 'uf+city-name'",
    type=str,
)
@click.option(
    "-m",
    "--max_pages",
    default=None,
    help="Max number of pages",
    type=int,
)
def main(action: str, estate_type: str, location: str, max_pages: int):
    """Main function. Set the directories, run the scrapper,
    format data and load to PostgreSQL database.
    """

    set_directories()

    search_estates(action, estate_type, location, max_pages)

    format_data()

    load()


if __name__ == "__main__":

    try:
        cli()

    except Exception as err:
        logger.error(err)
