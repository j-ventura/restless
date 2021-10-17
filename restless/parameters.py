from restless.util import FormData
from pydantic import BaseModel
from enum import Enum
from typing import ClassVar


class StringParameter(str):
    ENUM: Enum = None

    @classmethod
    def enum(cls, enum: Enum) -> ClassVar:
        return type(cls.__name__, (cls,), {'ENUM': enum})

    @classmethod
    def enum_keys(cls):
        return [k.strip('_') for k in cls.ENUM.__members__]


class PathParameter(StringParameter):
    LOCATION = 'path'


class QueryParameter(StringParameter):
    LOCATION = 'query'


class HeaderParameter(StringParameter):
    LOCATION = 'header'


class FormParameter(StringParameter):
    LOCATION = 'formData'


class FormFile(FormData.File):
    LOCATION = 'formData'


class BinaryParameter(bytes):
    LOCATION = 'body'


class BodyParameter(BaseModel):
    pass


class AuthorizerParameter(dict):
    pass
