import types
import traceback
from datetime import timezone
from typing import get_args, get_origin, Union

from loguru import logger
import pydantic


def suppress_errors_and_log(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            return None

    return wrapper


def datetime_to_iso8601_z(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def is_int_type(field_type):
    """
    Verifica se o tipo do campo é int ou Optional[int].
    """
    if field_type == int:
        return True

    origin = get_origin(field_type)
    if origin is Union:
        args = get_args(field_type)
        if int in args and type(None) in args:
            return True

    if isinstance(field_type, types.UnionType):
        args = get_args(field_type)
        if int in args and type(None) in args:
            return True

    return False


def get_integer_fields(class_: pydantic._internal._model_construction.ModelMetaclass):
    annotations = class_.__annotations__
    integer_columns = []
    for field_name, field_type in annotations.items():
        if is_int_type(field_type):
            integer_columns.append(field_name)
    return integer_columns
