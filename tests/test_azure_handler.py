from unittest import TestCase
from restless.interfaces.azure import FunctionHandler
from restless.parameters import QueryParameter
from azure.functions import HttpRequest


class TestHandler(TestCase):
    def testHeaders(self):
        handler = FunctionHandler()

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