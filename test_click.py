#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import unittest
import mock


class TestCases(unittest.TestCase):

    def test_init(self):
        import click
        self.assertIsNotNone(click)

    def test_load_templates(self):
        import click

        for template in [click.FISH,  click.BANANA, click.PIE,
                         click.LILIN, click.BEE,    click.POWERUP,
                         click.SKULL, click.DOWN,   click.UP,
                         click.GILD,  click.SHOP,   click.UPGRADE]:
            self.assertIsNotNone(template)

    def test_logit_decorator(self):
        from click import logit
        log = mock.Mock(spec=["error"])

        @logit(log)
        def failing_function():
            raise Exception("ERROR")

        failing_function()

        self.assertTrue(log.called)

if __name__ == '__main__':
    unittest.main()
