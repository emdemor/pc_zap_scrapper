import logging
import numpy as np
import pandas as pd
from loguru import logger
from geopy.geocoders import Nominatim
from tqdm import tqdm

from pc_zap_scrapper import PATH_NEIGHBORHOOD_COORDS


def get_coord(*args):

    maps_args = ", ".join(tuple(map(str, filter(lambda x: x is not None, args))))

    geoloc = Nominatim(user_agent="test_app")

    return geoloc.geocode(maps_args)


def get_estate_coord(state, city, neighbor, street, n_tries=10):

    result = None

    for i in range(n_tries):

        # Full address
        try:
            args = [state, city, neighbor, street]
            result = get_coord(*args)
            assert result is not None
            return result.point[:2]

        except AssertionError as err:
            logger.error(err)

        # Trying neighbor
        try:
            args = [state, city, neighbor]
            result = get_coord(*args)
            assert result is not None
            return result.point[:2]

        except AssertionError as err:
            logger.error(err)

        # Trying street
        try:
            args = [state, city, street]
            result = get_coord(*args)
            assert result is not None
            return result.point[:2]

        except AssertionError as err:
            logger.error(err)

        finally:
            return (np.nan, np.nan)


def get_lat_long(df, n_tries: int = 10):

    temp = df.copy()[~df["id_zap"].duplicated()]

    res = []
    for tup in tqdm(
        temp[["id_zap", "neighborhood", "street", "latitude", "longitude"]].values,
        total=len(temp),
    ):
        id_zap, neighbor, street, latitude, longitude = tup
        state, city = ("MG", "Poços de Caldas")

        result = {"id_zap": id_zap, "latitude": np.nan, "longitude": np.nan}

        try:

            if (not pd.isnull(latitude)) and (not pd.isnull(longitude)):

                result = {
                    "id_zap": id_zap,
                    "latitude": latitude,
                    "longitude": longitude,
                }

            else:
                new_latitude, new_longitude = get_estate_coord(
                    state, city, neighbor, street, n_tries=n_tries
                )

                if pd.isnull(latitude):
                    latitude = new_latitude

                if pd.isnull(longitude):
                    longitude = new_longitude

                result = {
                    "id_zap": id_zap,
                    "latitude": latitude,
                    "longitude": longitude,
                }

        except Exception as err:
            logging.error(err)

        res.append(result)

    filled_latlong = pd.DataFrame(res)

    cols = df.columns

    result = fill_latlong_missings(
        df.drop(columns=["latitude", "longitude"]).merge(
            filled_latlong,
            how="left",
            on="id_zap",
        )[cols]
    )

    return result


def fill_latlong_missings(df):

    temp = df.copy()

    neighbor_coords = pd.read_parquet(PATH_NEIGHBORHOOD_COORDS)

    temp = temp.merge(
        neighbor_coords, on="neighborhood", how="left", suffixes=("", "_neighbor")
    )
    temp["longitude"] = np.where(
        temp["longitude"].isna(), temp["longitude_neighbor"], temp["longitude"]
    )
    temp["latitude"] = np.where(
        temp["latitude"].isna(), temp["latitude_neighbor"], temp["latitude"]
    )
    temp = temp.drop(columns=["latitude_neighbor", "longitude_neighbor"])

    return temp
