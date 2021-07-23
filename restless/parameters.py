from restless.util import FormData
from pydantic import BaseModel


class StringParameter(str):
    pass


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
