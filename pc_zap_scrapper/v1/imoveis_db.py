import logging
import sqlalchemy
import pandas as pd
from tqdm import tqdm


def delete_by_search_id(engine: sqlalchemy.engine.base.Engine, search_id: str) -> None:
    """Delete a single record from pocos_de_caldas.imoveis database by search_id

    :param engine: SqlAlchemy engine
    :type engine: sqlalchemy.engine.base.Engine
    :param search_id: search_id to be deleted
    :type search_id: str
    """

    try:
        query = sqlalchemy.text(
            f"""
            DELETE FROM pocos_de_caldas.imoveis
            WHERE search_id = '{search_id}'
            """
        )

        result = engine.execute(query)

    except Exception as err:

        raise Exception(f"Not possible to delete search_id {search_id}", 400)


def load_interim_to_db(
    engine: sqlalchemy.engine.base.Engine,
    df_interim: pd.DataFrame,
    if_exists: str = "append",
):
    """Load interim to database

    :param engine: SqlAlchemy engine
    :type engine: sqlalchemy.engine.base.Engine
    :param df_interim: Dataframe with the data
    :type df_interim: pd.DataFrame
    :param if_exists: What to do if table exist. can be 'append' or 'fail', defaults to "append"
    :type if_exists: str, optional
    """

    for i in tqdm(range(len(df_interim))):

        temp = df_interim.iloc[i : i + 1]

        try:
            temp.to_sql(
                "imoveis",
                engine,
                schema="pocos_de_caldas",
                if_exists=if_exists,
                index=False,
            )

        except Exception as err:
            logging.error(err)
