from restless import Handler
from restless.util import camel_to_snake, snake_to_camel
from restless.openapi import make_spec, Formats
import json
from urllib.parse import unquote_plus
from flask import Response as FResponse
from flask import Flask, request
import os
from werkzeug.exceptions import BadRequest
from pydantic import BaseModel
from restless.parameters import PathParameter

THIS_FOLDER = os.path.dirname(__file__)


class Request:
    IN = "body"
    TYPE = dict

    @property
    def authorizer(self) -> dict:
        return dict(token=self.headers.get("Authorization", ''))

    def __init__(self, value, use_camel_case=True):
        self.path = unquote_plus(value.full_path.strip('?'))

        try:
            self.body = value.get_json(force=True)
        except BadRequest:
            self.body = value.data

        self.body = value.data
        self.method = value.method
        self.headers = value.headers
        self.query = value.args

        if use_camel_case:
            for member in ['body', 'headers', 'query']:
                setattr(self, member, camel_to_snake(getattr(self, member)))


class Response(FResponse):
    def __init__(self, body="", status_code=200, headers=None, use_camel_case=True):
        self.status_code = status_code
        self.headers = headers

        if isinstance(body, (bytes, str)):
            super().__init__(
                response=body,
                status=status_code,
                headers=headers
            )
            self.body = body
        elif isinstance(body, dict):
            super().__init__(
                response=snake_to_camel(body) if use_camel_case else json.dumps(body),
                status=status_code,
                headers=headers
            )
            self.body = self.response
        elif isinstance(body, BaseModel):
            super().__init__(
                response=json.dumps(snake_to_camel(body.dict())) if use_camel_case else json.dumps(body.dict()),
                status=status_code,
                headers=headers
            )
            self.body = self.response

        else:
            raise Exception("Unsupported")


class FlaskHandler(Handler):
    DATA_FORMAT = 'yml'
    REQUEST = Request
    RESPONSE = Response

    def __init__(
            self, name, description, version, security=None, default_security=None, camel_case_interface=True
    ):
        self.security = security or []
        self.default_security = default_security or []
        self.name = name
        self.description = description
        self.version = version

        super().__init__(use_camel_case=camel_case_interface)

        self.schemes = ["http", "https"]

        app = Flask(__name__)

        @self.handle("get", "/spec/swagger.<extension>")
        def spec(extension: PathParameter.enum(Formats)) -> {200: str}:
            return make_spec(
                self.name,
                self.description,
                self.version,
                self,
                security=self.security,
                default_security=self.default_security,
                file_name=None,
                data_format=extension
            )

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def catch_all(path):
            return self(request)

        self.app = app
