import unittest

class TestCases(unittest.TestCase):

    def test_init(self):
        import click
        self.assertIsNotNone(click)
