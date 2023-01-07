import logging
from dotenv import load_dotenv
from pc_zap_scrapper.load import load
from pc_zap_scrapper.scrap import search_estates
from pc_zap_scrapper.transform import format_data
from pc_zap_scrapper import ACTION, LOCALIZATION, TYPE

def main():
    """ Main function"""

    try:
        assert load_dotenv()

        search_estates(ACTION, TYPE, LOCALIZATION)

        format_data()

        load()

    except Exception as err:
        logging.error(err)


if __name__ == "__main__":
    main()
