from unittest import TestCase
from restless import Handler
from restless.interfaces.azure import Response, Request
from restless.parameters import PathParameter, QueryParameter, HeaderParameter, FormFile, FormParameter, \
    BinaryParameter, BodyParameter
from restless.errors import Forbidden, Unauthorized, Missing
import requests
from base64 import b64encode
import json
from datetime import datetime
from typing import List, Optional
from azure.functions import HttpRequest


class TestHandler(TestCase):
    def testHeaders(self):
        handler = Handler(Request, Response)

        @handler.handle('post', '/some/generator')
        def get_generator(parameter: QueryParameter = "1") -> {200: dict}:
            return {"parameter_value": parameter}, 200, {"A": "B"}

        out = handler(
            HttpRequest(
                method='post',
                url='https://.*/api/some/generator',
                body=b''
            )
        )

        self.assertEqual(
            {
                'statusCode': 200,
                'headers': {'a': 'B', 'content-type': 'application/json'},
                'body': '{"parameter_value": "1"}'
            },
            out.dict
        )

    # def testStatusCode(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('post', '/some/generator')
    #     def get_generator(parameter: QueryParameter = "1") -> {201: dict}:
    #         return {"parameter_value": parameter}, 201
    #
    #     out = handler(
    #         {
    #             "path": "/some/generator",
    #             "httpMethod": 'post'
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 201,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"parameter_value": "1"}'
    #         },
    #         out
    #     )
    #
    # def testUnknownOutput(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/generator')
    #     def get_generator(parameter: QueryParameter = "1") -> {200: dict}:
    #         return "some string"
    #
    #     self.assertRaises(
    #         AssertionError,
    #         handler,
    #         {
    #             "path": "/some/generator",
    #             "httpMethod": 'get'
    #         }
    #     )
    #
    # def testReturnGenerator(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/generator')
    #     def get_generator(parameter: QueryParameter = "1") -> {200: [dict]}:
    #         yield {"parameter_value": parameter}
    #         yield {"parameter_value": parameter}
    #
    #     out = handler(
    #         {
    #             "path": "/some/generator",
    #             "httpMethod": 'get'
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 200,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '[{"parameter_value": "1"}, {"parameter_value": "1"}]'
    #         },
    #         out
    #     )
    #
    # def testBodyParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     class User(BodyParameter):
    #         id: int
    #         name = 'John Doe'
    #         signup_ts: Optional[datetime] = None
    #         friends: List[int] = []
    #
    #     @handler.handle('post', '/some/body')
    #     def get_basic(user: User) -> {200: dict}:
    #         return {"parameter_value": user}
    #
    #     with self.subTest('OK'):
    #         out = handler(
    #             {
    #                 "path": "/some/body",
    #                 "httpMethod": 'post',
    #                 'body': json.dumps(
    #                     {
    #                         'id': '123',
    #                         'signup_ts': '2019-06-01 12:22',
    #                         'friends': [1, 2, '3'],
    #                     }
    #                 )
    #             }
    #         )
    #
    #         self.assertEqual(
    #             200,
    #             out["statusCode"]
    #         )
    #
    #     with self.subTest('BAD'):
    #         out = handler(
    #             {
    #                 "path": "/some/body",
    #                 "httpMethod": 'post',
    #                 'body': json.dumps(
    #                     {
    #                         'signup_ts': '2019-06-01 12:22',
    #                         'friends': [1, 2, '3'],
    #                     }
    #                 )
    #             }
    #         )
    #
    #         self.assertEqual(
    #             400,
    #             out["statusCode"]
    #         )
    #
    # def testOptionalParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/optional')
    #     def get_basic(parameter: QueryParameter = "1") -> {200: dict}:
    #         return {"parameter_value": parameter}
    #
    #     @handler.handle('get', '/some/required')
    #     def get_basic(parameter: QueryParameter) -> {200: dict}:
    #         return {"parameter_value": parameter}
    #
    #     with self.subTest('Optional'):
    #         out = handler(
    #             {
    #                 "path": "/some/optional",
    #                 "httpMethod": 'get'
    #             }
    #         )
    #
    #         self.assertEqual(
    #             {
    #                 'statusCode': 200,
    #                 'headers': {'Content-Type': 'application/json'},
    #                 'isBase64Encoded': False,
    #                 'body': '{"parameter_value": "1"}'
    #             },
    #             out
    #         )
    #
    #     with self.subTest('Required'):
    #         out = handler(
    #             {
    #                 "path": "/some/required",
    #                 "httpMethod": 'get'
    #             }
    #         )
    #
    #         self.assertEqual(
    #             {
    #                 'statusCode': 400,
    #                 'headers': {'Content-Type': 'application/json'},
    #                 'isBase64Encoded': False,
    #                 'body': '{"error": "get_basic() missing 1 required positional argument: \'parameter\'"}'
    #             },
    #             out
    #         )
    #
    # def testExceptions(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/Forbidden')
    #     def forbidden(parameter: QueryParameter) -> {200: dict}:
    #         raise Forbidden("Forbidden")
    #
    #     @handler.handle('get', '/some/Unauthorized')
    #     def unauthorized(parameter: QueryParameter) -> {200: dict}:
    #         raise Unauthorized("Unauthorized")
    #
    #     @handler.handle('get', '/some/Missing')
    #     def unauthorized(parameter: QueryParameter) -> {200: dict}:
    #         raise Missing("Missing")
    #
    #     for endpoint, status_code in [
    #         ('Forbidden', 403),
    #         ('Unauthorized', 401),
    #         ('Missing', 404)
    #     ]:
    #         with self.subTest(endpoint):
    #             out = handler(
    #                 {
    #                     "path": "/some/" + endpoint,
    #                     "httpMethod": 'get',
    #                     "queryStringParameters": {
    #                         "parameter": "1"
    #                     }
    #                 }
    #             )
    #
    #             self.assertEqual(
    #                 {
    #                     'statusCode': status_code,
    #                     'headers': {'Content-Type': 'application/json'},
    #                     'isBase64Encoded': False,
    #                     'body': f'{{"error": "{endpoint}"}}'
    #                 },
    #                 out
    #             )
    #
    # def testBinaryParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('post', '/some/path')
    #     def get_basic(parameter: BinaryParameter) -> {200: dict}:
    #         return {"parameter_value": parameter.decode()}
    #
    #     out = handler(
    #         {
    #             "path": "/some/path",
    #             "httpMethod": 'post',
    #             "body": b64encode(b'ABC').decode(),
    #             'isBase64Encoded': True
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 200,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"parameter_value": "ABC"}'
    #         },
    #         out
    #     )
    #
    # def testFormsParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('post', '/some/path')
    #     def get_basic(file: FormFile, form_parameter: FormParameter) -> {200: dict}:
    #         return {"parameter_value": form_parameter, "size": len(file.data)}
    #
    #     req = requests.Request(
    #         files={
    #             'file': ('test.dat', b'ABC', 'application/octet-stream')
    #         },
    #         data={
    #             "form_parameter": "1"
    #         },
    #         url='https://myapi',
    #         method='post'
    #     )
    #
    #     req = req.prepare()
    #
    #     out = handler(
    #         {
    #             "path": "/some/path",
    #             "httpMethod": 'post',
    #             "body": b64encode(req.body).decode(),
    #             "isBase64Encoded": True
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 200,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"parameter_value": "1", "size": 3}'
    #         },
    #         out
    #     )
    #
    # def testHeaderParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/path')
    #     def get_basic(parameter: HeaderParameter) -> {200: dict}:
    #         return {"parameter_value": parameter}
    #
    #     out = handler(
    #         {
    #             "path": "/some/path",
    #             "httpMethod": 'get',
    #             "headers": {
    #                 "parameter": "1"
    #             }
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 200,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"parameter_value": "1"}'
    #         },
    #         out
    #     )
    #
    # def testQueryParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/path')
    #     def get_basic(parameter: QueryParameter) -> {200: dict}:
    #         return {"parameter_value": parameter}
    #
    #     out = handler(
    #         {
    #             "path": "/some/path",
    #             "httpMethod": 'get',
    #             "queryStringParameters": {
    #                 "parameter": "1"
    #             }
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 200,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"parameter_value": "1"}'
    #         },
    #         out
    #     )
    #
    # def testPathParameter(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/path/<parameter>')
    #     def get_basic(parameter: PathParameter) -> {200: dict}:
    #         return {"parameter_value": parameter}
    #
    #     out = handler(
    #         {
    #             "path": "/some/path/1",
    #             "httpMethod": 'get'
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 200,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"parameter_value": "1"}'
    #         },
    #         out
    #     )
    #
    # def testNotFound(self):
    #     handler = Handler(Request, Response)
    #
    #     @handler.handle('get', '/some/other/path/<parameter>')
    #     def get_basic(parameter) -> {200: dict}:
    #         return {}
    #
    #     out = handler(
    #         {
    #             "path": "/some/path/1",
    #             "httpMethod": 'get'
    #         }
    #     )
    #
    #     self.assertEqual(
    #         {
    #             'statusCode': 404,
    #             'headers': {'Content-Type': 'application/json'},
    #             'isBase64Encoded': False,
    #             'body': '{"error": "Missing \'get\' on \'/some/path/1\'"}'
    #         },
    #         out
    #     )
    #
    # def testOverlapping(self):
    #     handler = Handler(Request, Response)
    #
    #     paths = [
    #         '/some/other/path/<parameter>',
    #         '/some/other/other/<parameter>',
    #         '/some/other/<parameter>',
    #         '/some/<parameter>'
    #     ]
    #
    #     for path in paths:
    #         @handler.handle('get', path)
    #         def get_basic(parameter: PathParameter) -> {200: dict}:
    #             return {"parameter_value": parameter}
    #
    #     for idx, path in enumerate(paths):
    #         with self.subTest(path.replace('<parameter>', str(idx))):
    #             out = handler(
    #                 {
    #                     "path": path.replace('<parameter>', str(idx)),
    #                     "httpMethod": 'get'
    #                 }
    #             )
    #
    #             self.assertEqual(
    #                 {
    #                     'statusCode': 200,
    #                     'headers': {'Content-Type': 'application/json'},
    #                     'isBase64Encoded': False,
    #                     'body': f'{{"parameter_value": "{idx}"}}'
    #                 },
    #                 out
    #             )
