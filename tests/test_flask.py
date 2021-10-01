from restless.security import ApiKeyAuth
from restless.parameters import BodyParameter
from restless.interfaces.flask_app import FlaskHandler
from unittest import TestCase
import os
import json
import yaml

os.chdir(os.path.dirname(__file__))


class Message(BodyParameter):
    text: str


class TestRouter(TestCase):
    def setUp(self) -> None:
        self.handler = FlaskHandler(
            "Test API",
            "meh",
            "0.1",
            security=[
                ApiKeyAuth(ApiKeyAuth.In.header, name='Authorization')
            ]
        )

        self.client = self.handler.app.test_client()

    def test_basic(self):
        @self.handler.handle("get", "/")
        def root() -> {200: Message}:
            return Message(text="all cool")

        out = self.client.get('/')

        self.assertEqual(200, out.status_code, out.data)

        self.assertEqual(
            {'text': 'all cool'},
            json.loads(out.data)
        )

    def test_spec(self):
        @self.handler.handle("get", "/")
        def root() -> {200: Message}:
            return Message(text="all cool")

        out = self.client.get('/spec/swagger.json')

        self.assertEqual(200, out.status_code, out.data)

        self.assertEqual(
            {'components': {'schemas': {'Error': {'properties': {'details': {'type': 'object'},
                                                                 'error': {'type': 'string'}},
                                                  'required': ['error']},
                                        'Message': {'properties': {'text': {'title': 'Text',
                                                                            'type': 'string'}},
                                                    'required': ['text'],
                                                    'title': 'Message',
                                                    'type': 'object'}},
                            'securitySchemes': {'Authorization': {'in': 'header',
                                                                  'name': 'Authorization',
                                                                  'type': 'apiKey'}}},
             'info': {'description': 'meh', 'title': 'Test API', 'version': '0.1'},
             'openapi': '3.0.0',
             'paths': {'/': {'get': {'description': 'root',
                                     'parameters': [],
                                     'responses': {'200': {'content': {
                                         'application/json': {'schema': {'$ref': '#/components/schemas/Message'}}},
                                                           'description': 'meh'},
                                                   '400': {'content': {'application/json': {
                                                       'schema': {'$ref': '#/components/schemas/Error'}}},
                                                           'description': 'Bad Request'},
                                                   '401': {'content': {'application/json': {
                                                       'schema': {'$ref': '#/components/schemas/Error'}}},
                                                           'description': 'Unauthorized'},
                                                   '403': {'content': {'application/json': {
                                                       'schema': {'$ref': '#/components/schemas/Error'}}},
                                                           'description': 'Forbidden'},
                                                   '404': {'content': {'application/json': {
                                                       'schema': {'$ref': '#/components/schemas/Error'}}},
                                                           'description': 'Not Found'}},
                                     'tags': ['']}}},
             'servers': [],
             'tags': []},
            yaml.load(out.data, Loader=yaml.SafeLoader)
        )
