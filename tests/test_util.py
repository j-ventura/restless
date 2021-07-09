from omnirest.util import camel_to_snake, snake_to_camel
from unittest import TestCase


class TestCases(TestCase):
    def test_camel_to_snake(self):
        for case in [
            ('single', 'single'),
            ('simpleCase', 'simple_case'),
            ('simpleURL', 'simple_url'),
            (
                    {"someKeyYeyA": {"deeeperKey": "value", "listKey": ["A", {"someKey": "someValue"}]}},
                    {"some_key_yey_a": {"deeeper_key": "value", "list_key": ["A", {"some_key": "someValue"}]}}
            )
        ]:
            with self.subTest(case[0]):
                self.assertEqual(
                    case[1],
                    camel_to_snake(case[0])
                )

    def test_snake_to_camel(self):
        for case in [
            ('single', 'single'),
            ('simpleCase', 'simple_case'),
            ('simpleUrl', 'simple_url'),
            (
                    {"someKeyYeyA": {"deeeperKey": "value", "listKey": ["a", {"someKey": "someValue"}]}},
                    {"some_key_yey_a": {"deeeper_key": "value", "list_key": ["a", {"some_key": "someValue"}]}}
            )
        ]:
            with self.subTest(case[1]):
                self.assertEqual(
                    case[0],
                    snake_to_camel(case[1])
                )
