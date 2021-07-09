from unittest import TestCase
from omnirest.interfaces import azure, aws
from base64 import b64encode


class TestAWS(TestCase):
    def test_input(self):
        r = aws.Request(
            {
                "resource": "/my/path",
                "path": "/my/path",
                "httpMethod": "GET",
                "headers": {
                    "header1": "value1",
                    "header2": "value2"
                },
                "multiValueHeaders": {
                    "header1": [
                        "value1"
                    ],
                    "header2": [
                        "value1",
                        "value2"
                    ]
                },
                "queryStringParameters": {
                    "parameter1": "value1",
                    "parameter2": "value"
                },
                "multiValueQueryStringParameters": {
                    "parameter1": [
                        "value1",
                        "value2"
                    ],
                    "parameter2": [
                        "value"
                    ]
                },
                "requestContext": {
                    "accountId": "123456789012",
                    "apiId": "id",
                    "authorizer": {
                        "claims": None,
                        "scopes": None
                    },
                    "domainName": "id.execute-api.us-east-1.amazonaws.com",
                    "domainPrefix": "id",
                    "extendedRequestId": "request-id",
                    "httpMethod": "GET",
                    "identity": {
                        "accessKey": None,
                        "accountId": None,
                        "caller": None,
                        "cognitoAuthenticationProvider": None,
                        "cognitoAuthenticationType": None,
                        "cognitoIdentityId": None,
                        "cognitoIdentityPoolId": None,
                        "principalOrgId": None,
                        "sourceIp": "IP",
                        "user": None,
                        "userAgent": "user-agent",
                        "userArn": None,
                        "clientCert": {
                            "clientCertPem": "CERT_CONTENT",
                            "subjectDN": "www.example.com",
                            "issuerDN": "Example issuer",
                            "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                            "validity": {
                                "notBefore": "May 28 12:30:02 2019 GMT",
                                "notAfter": "Aug  5 09:36:04 2021 GMT"
                            }
                        }
                    },
                    "path": "/my/path",
                    "protocol": "HTTP/1.1",
                    "requestId": "id=",
                    "requestTime": "04/Mar/2020:19:15:17 +0000",
                    "requestTimeEpoch": 1583349317135,
                    "resourceId": None,
                    "resourcePath": "/my/path",
                    "stage": "$default"
                },
                "pathParameters": None,
                "stageVariables": None,
                "body": '{"A":"B"}',
                "isBase64Encoded": False
            }
        )

        self.assertEqual(
            {
                'authorizer': {'claims': None, 'scopes': None},
                'body': {'a': 'B'},
                'headers': {'header1': 'value1', 'header2': 'value2'},
                'method': 'GET',
                'path': '/my/path',
                'query': {'parameter1': 'value1', 'parameter2': 'value'}
            },
            r.__dict__
        )

    def test_binary_input(self):
        r = aws.Request(
            {
                "resource": "/my/path",
                "path": "/my/path",
                "httpMethod": "GET",
                "headers": {
                    "header1": "value1",
                    "header2": "value2"
                },
                "multiValueHeaders": {
                    "header1": [
                        "value1"
                    ],
                    "header2": [
                        "value1",
                        "value2"
                    ]
                },
                "queryStringParameters": {
                    "parameter1": "value1",
                    "parameter2": "value"
                },
                "multiValueQueryStringParameters": {
                    "parameter1": [
                        "value1",
                        "value2"
                    ],
                    "parameter2": [
                        "value"
                    ]
                },
                "requestContext": {
                    "accountId": "123456789012",
                    "apiId": "id",
                    "authorizer": {
                        "claims": None,
                        "scopes": None
                    },
                    "domainName": "id.execute-api.us-east-1.amazonaws.com",
                    "domainPrefix": "id",
                    "extendedRequestId": "request-id",
                    "httpMethod": "GET",
                    "identity": {
                        "accessKey": None,
                        "accountId": None,
                        "caller": None,
                        "cognitoAuthenticationProvider": None,
                        "cognitoAuthenticationType": None,
                        "cognitoIdentityId": None,
                        "cognitoIdentityPoolId": None,
                        "principalOrgId": None,
                        "sourceIp": "IP",
                        "user": None,
                        "userAgent": "user-agent",
                        "userArn": None,
                        "clientCert": {
                            "clientCertPem": "CERT_CONTENT",
                            "subjectDN": "www.example.com",
                            "issuerDN": "Example issuer",
                            "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                            "validity": {
                                "notBefore": "May 28 12:30:02 2019 GMT",
                                "notAfter": "Aug  5 09:36:04 2021 GMT"
                            }
                        }
                    },
                    "path": "/my/path",
                    "protocol": "HTTP/1.1",
                    "requestId": "id=",
                    "requestTime": "04/Mar/2020:19:15:17 +0000",
                    "requestTimeEpoch": 1583349317135,
                    "resourceId": None,
                    "resourcePath": "/my/path",
                    "stage": "$default"
                },
                "pathParameters": None,
                "stageVariables": None,
                "body": b64encode(b'ABC').decode(),
                "isBase64Encoded": True
            }
        )

        self.assertEqual(
            {
                'authorizer': {'claims': None, 'scopes': None},
                'body': b'ABC',
                'headers': {'header1': 'value1', 'header2': 'value2'},
                'method': 'GET',
                'path': '/my/path',
                'query': {'parameter1': 'value1', 'parameter2': 'value'}
            },
            r.__dict__
        )

    def test_output(self):
        out = aws.Response('{"A":"B"}', 200)

        self.assertEqual(
            {
                'statusCode': 200,
                'headers': {},
                'isBase64Encoded': False,
                'body': '{"A":"B"}'
            },
            out
        )

    def test_json_output(self):
        out = aws.Response({"A": "B"}, 200)

        self.assertEqual(
            {
                'body': '{"A": "B"}',
                'headers': {'Content-Type': 'application/json'},
                'isBase64Encoded': False,
                'statusCode': 200
            },
            out
        )

    def test_binary_output(self):
        out = aws.Response(b'ABC', 200)

        self.assertEqual(
            {
                'body': 'QUJD',
                'headers': {},
                'isBase64Encoded': True,
                'statusCode': 200
            },
            out
        )


class TestAzure(TestCase):
    def test_input(self):
        r = azure.Request(
            azure.HttpRequest(
                body=b'{"A":"B"}',
                method="get",
                url="https://some_function/api/my/path",
                headers={'header1': 'value1', 'header2': 'value2'},
                params={'parameter1': 'value1', 'parameter2': 'value'}
            )
        )

        self.assertEqual(
            {
                'body': {'a': 'B'},
                'headers': {'header1': 'value1', 'header2': 'value2'},
                'method': 'GET',
                'path': '/my/path',
                'query': {'parameter1': 'value1', 'parameter2': 'value'}
            },
            r.__dict__
        )

    def test_binary_input(self):
        r = azure.Request(
            azure.HttpRequest(
                body=b'ABC',
                method="get",
                url="https://some_function/api/my/path",
                headers={'header1': 'value1', 'header2': 'value2'},
                params={'parameter1': 'value1', 'parameter2': 'value'}
            )
        )

        self.assertEqual(
            {
                'body': b'ABC',
                'headers': {'header1': 'value1', 'header2': 'value2'},
                'method': 'GET',
                'path': '/my/path',
                'query': {'parameter1': 'value1', 'parameter2': 'value'}
            },
            r.__dict__
        )

    def test_output(self):
        out = azure.Response(body='{"A":"B"}', status_code=200)

        self.assertEqual(
            b'{"A":"B"}',
            out.get_body()
        )

        self.assertEqual(
            200,
            out.status_code
        )

    def test_json_output(self):
        out = azure.Response(body={"A": "B"}, status_code=200)

        self.assertEqual(
            b'{"A": "B"}',
            out.get_body()
        )

        self.assertEqual(
            200,
            out.status_code
        )

        self.assertEqual(
            "application/json",
            out.headers["Content-Type"]
        )

    def test_binary_output(self):
        out = azure.Response(body=b'ABC', status_code=200)

        self.assertEqual(
            b'ABC',
            out.get_body()
        )

        self.assertEqual(
            200,
            out.status_code
        )
