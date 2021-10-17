from restless.security import ApiKeyAuth
from restless.parameters import BodyParameter, AuthorizerParameter
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
        @self.handler.handle("get", "/secured")
        def secured(auth: AuthorizerParameter) -> {200: Message}:
            return Message(text=auth['token'])

        @self.handler.handle("get", "/")
        def secured() -> {200: Message}:
            return Message(text="all cool other")

        out = self.client.get('/secured', headers={'Authorization': 'meh'})

        self.assertEqual(200, out.status_code, out.data)

        self.assertEqual(
            {'text': 'meh'},
            json.loads(out.data)
        )