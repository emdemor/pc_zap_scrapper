import logging
import os
from loguru import logger
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pc_zap_scrapper import PATH_DATA_INTERIM, PATH_TEMP_DOTENV, ENV_VARS
from pc_zap_scrapper.imoveis_db import load_interim_to_db


def load():

    if not load_dotenv(dotenv_path=PATH_TEMP_DOTENV):
        error_message = "No '.env' file was found."
        logger.error(error_message)
        raise Exception(error_message)

    for envvar in ENV_VARS:
        if os.getenv(envvar) is None:
            error_message = f"Environment variable {envvar} not found"
            logger.error(error_message)
            raise Exception(error_message)

    uri = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )

    engine = create_engine(uri)

    df_interim = pd.read_parquet(PATH_DATA_INTERIM)

    load_interim_to_db(engine, df_interim)


if __name__ == "__main__":

    try:
        assert load_dotenv()
        load()
    except Exception as err:
        logging.error(err)
