import logging
import os
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
from dotenv import load_dotenv
from pc_zap_scrapper import PATH_DATA_INTERIM
from pc_zap_scrapper.imoveis_db import load_interim_to_db


def load():

    engine = create_engine(
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
        )
    )

    df_interim = pd.read_parquet(PATH_DATA_INTERIM)

    load_interim_to_db(engine, df_interim)


if __name__ == "__main__":

    try:
        assert load_dotenv()
        load()
    except Exception as err:
        logging.error(err)
