from enum import Enum


class ModelType(Enum):
    """
    Enum for model types.
    """
    PEEWEE = "peewee"
    SQLMODEL = "sqlmodel"
    TORTOISE = "tortoise"
    PYDANTIC = "pydantic"
