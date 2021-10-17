from unittest import TestCase
from restless import Handler
from restless.interfaces.aws import LambdaHandler
from restless.parameters import PathParameter, QueryParameter, HeaderParameter, FormFile, FormParameter, \
    BinaryParameter, BodyParameter
from datetime import datetime
from typing import List, Optional
from restless.openapi import make_spec
from restless.security import ApiKeyAuth
import yaml
from deepdiff import DeepDiff
import os

os.chdir(os.path.dirname(__file__))


class TestSpec(TestCase):
    def testAWS(self):
        handler = LambdaHandler()

        @handler.handle('post', '/some/query')
        def get_query(parameter: QueryParameter = "1") -> {201: dict}:
            """Using Query"""
            return {"parameter_value": parameter}, 200, {"A": "B"}

        @handler.handle('get', '/some/generator')
        def get_generator(parameter: QueryParameter = "1") -> {200: [dict]}:
            """Returning Generator"""
            yield {"parameter_value": parameter}
            yield {"parameter_value": parameter}

        class User(BodyParameter):
            id: int
            name = 'John Doe'
            signup_ts: Optional[datetime] = None
            friends: List[int] = []

        @handler.handle('post', '/some/body')
        def get_object(user: User) -> {200: User}:
            """Object I/O"""
            return {"parameter_value": user}

        @handler.handle('post', '/base/path')
        def get_basic(parameter: BinaryParameter) -> {200: dict}:
            """Binary Parameter"""
            return {"parameter_value": parameter.decode()}

        @handler.handle('post', '/some/other/form', tags=['A'])
        def get_basic(file: FormFile, form_parameter: FormParameter) -> {200: dict}:
            """Form Parameters"""
            return {"parameter_value": form_parameter, "size": len(file.data)}

        @handler.handle('get', '/some/path/<parameter>', security=['token'])
        def get_basic(parameter: PathParameter) -> {200: dict}:
            """Path Parameters"""
            return {"parameter_value": parameter}

        @handler.handle('post', '/some/binary', security=False)
        def post_binary(parameter: BinaryParameter) -> {200: dict}:
            """Binary Parameter"""
            return {"parameter_value": parameter.decode()}

        @handler.handle('post', '/some/header', security=False)
        def post_binary(parameter: HeaderParameter) -> {200: dict}:
            """Header Parameter"""
            return {"parameter_value": parameter}

        with self.subTest('Regular'):
            make_spec(
                'The API',
                'Some description',
                '0.0.1',
                handler,
                security=[
                    ApiKeyAuth(ApiKeyAuth.In.header, name='Authorization'),
                    ApiKeyAuth(ApiKeyAuth.In.query, name='token')
                ],
                default_security=['Authorization'],
                file_name='new_aws.yaml'
            )

            with open('spec.yaml') as fixture, open('new_aws.yaml') as test:
                difference = DeepDiff(
                    yaml.load(fixture, Loader=yaml.SafeLoader),
                    yaml.load(test, Loader=yaml.SafeLoader)
                )

            self.assertEqual(
                {},
                difference,
                difference
            )

        with self.subTest('Camel Cased'):
            handler.use_camel_case = True

            make_spec(
                'The API',
                'Some description',
                '0.0.1',
                handler,
                security=[
                    ApiKeyAuth(ApiKeyAuth.In.header, name='Authorization'),
                    ApiKeyAuth(ApiKeyAuth.In.query, name='token')
                ],
                default_security=['Authorization'],
                file_name='new_aws.yaml'
            )

            with open('camel_spec.yaml') as fixture, open('new_aws.yaml') as test:
                difference = DeepDiff(
                    yaml.load(fixture, Loader=yaml.SafeLoader),
                    yaml.load(test, Loader=yaml.SafeLoader)
                )

            self.assertEqual(
                {},
                difference,
                difference
            )
