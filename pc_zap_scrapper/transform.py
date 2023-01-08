import json
import logging
import pandas as pd
import numpy as np
import pandasql
from loguru import logger

from pc_zap_scrapper import PATH_DATA_INTERIM, PATH_DATA_RAW
from pc_zap_scrapper.maps import get_lat_long

VARCHAR_LENGTHS = {
    "search_id": 50,
    "id_zap": 20,
    "type": 28,
    "state": 3,
    "city": 33,
    "neighborhood": 50,
}

PSQL_TYPES = [
    {
        "num_type": "int",
        "type_name": "smallint",
        "range": [-int((2**16) / 2), int((2**16) / 2 - 1)],
        "pd_type": "Int16",
    },
    {
        "num_type": "int",
        "type_name": "integer",
        "range": [-int((2**32) / 2), int((2**32) / 2 - 1)],
        "pd_type": "Int32",
    },
    {
        "num_type": "int",
        "type_name": "bigint",
        "range": [-int((2**64) / 2), int((2**64) / 2 - 1)],
        "pd_type": "Int64",
    },
    {
        "num_type": "real",
        "type_name": "real",
        "range": None,
        "pd_type": "Float32",
    },
    {
        "num_type": "real",
        "type_name": "double precision",
        "range": None,
        "pd_type": "Float64",
    },
    {
        "num_type": "string",
        "type_name": "varchar",
        "range": None,
        "pd_type": "string",
    },
]

QUERY = """
    select
        search_id,
        id as id_zap,
        date(search_date) as search_date,
        --createdat as creation_date,
        --updatedat as last_update,
        unittypes as type,
        parkingspaces as n_parking_spaces,
        bathrooms as n_bathrooms,
        bedrooms as n_bedrooms,
        usableareas as area,
        floors as n_floors,
        unitsonthefloor as units_on_floor,
        suites as n_suites,
        --search_localization,
        address_stateacronym as state,
        address_city as city,
        --address_zone as zone,
        address_neighborhood as neighborhood,
        address_street as street,
        cast(point_lon as real) as longitude,
        cast(point_lat as real) as latitude,
        cast(pricinginfos_price as real) as price,
        cast(pricinginfos_monthlycondofee as real) condo_fee,
        cast(pricinginfos_yearlyiptu as real) as iptu,
        resale,
        buildings,
        case
            when (constructionstatus = 'PLAN_ONLY') then 1
            else 0
        end as plan_only,
        amenities,
        address_poislist as pois_list,
        link,
        description
    from zap_imoveis
    where address_city like '%oços%'
    """

NUMERICAL_COLUMNS = [
    "n_parking_spaces",
    "n_bathrooms",
    "n_bedrooms",
    "area",
    "n_floors",
    "units_on_floor",
    "n_suites",
    "longitude",
    "latitude",
    "price",
    "condo_fee",
    "iptu",
    "resale",
    "buildings",
    "plan_only",
]

SMALLINT_COLUMNS = [
    "area",
    "n_parking_spaces",
    "n_bathrooms",
    "n_bedrooms",
    "n_floors",
    "units_on_floor",
    "n_suites",
    "resale",
    "buildings",
    "plan_only",
]


def __check_type_psql(kwargs, type_):
    if type_ in kwargs:
        if type(kwargs[type_]) == list:
            return True
        else:
            raise Exception('Type "list" is expected for the argument {type}')
    return False


def __check_value_out_of_range(column, range_):
    name = column.name
    if not column.between(*range_).all():
        logging.warning(
            f"Some values of {name} are out of range {range_}."
            + " We are clipping this values."
        )


def format_table_psql(df: pd.DataFrame):

    zap_imoveis = df.copy()

    df = pandasql.sqldf(QUERY)

    # Convertendo colunas numéricas
    for col in NUMERICAL_COLUMNS:
        try:
            df[col] = df[col].replace("", "NaN").replace("None", np.nan).astype(float)
        except Exception as err:
            logger.error(
                f"It was not possible to convert column {col} to float."
                + str(err)
            )

    # Convertendo colunas de datas
    df["search_date"] = df["search_date"].astype(str)

    # Formatando coluna de amenities
    df["amenities"] = df["amenities"].apply(interpret_amenities)

    # Formatando coluna pois_list
    df["pois_list"] = (
        df["pois_list"]
        .replace("None", np.nan)
        .str.split("|")
        .apply(interpret_pois_list)
    )

    kwargs = {"smallint": SMALLINT_COLUMNS}

    for elem in PSQL_TYPES:
        num_type = elem["num_type"]
        type_name = elem["type_name"]
        pd_type = elem["pd_type"]

        status = __check_type_psql(kwargs, type_name)

        if status:

            columns = kwargs[type_name]

            for col in columns:

                if num_type == "int":
                    __check_value_out_of_range(df[col], elem["range"])

                    df[col] = np.where(
                        df[col].notna(),
                        df[col].fillna(0).astype("Float64").clip(*elem["range"]),
                        np.nan,
                    )

                    df[col] = df[col].astype(pd_type)

                else:
                    df[col] = df[col].astype(pd_type)

    df["longitude"] = np.where(df["longitude"].abs() < 1, np.nan, df["longitude"])

    df["latitude"] = np.where(df["latitude"].abs() < 1, np.nan, df["latitude"])

    df["street"] = df["street"].fillna(np.nan)

    df = df[~df["search_id"].duplicated()]

    return df


def interpret_amenities(x):
    if (type(x) == float) | (x is None):
        return json.dumps([])
    else:
        return json.dumps(x.replace(" ", "").split("|"))


def interpret_pois_list(x):
    if type(x) == float:
        return json.dumps([])
    else:
        return json.dumps([dict(zip(["class", "name"], y.split(":"))) for y in x])


def format_data():
    df = pd.read_parquet(PATH_DATA_RAW)

    df = format_table_psql(df)

    df = get_lat_long(df)

    df.to_parquet(PATH_DATA_INTERIM)
