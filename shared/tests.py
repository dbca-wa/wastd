# -*- coding: utf-8 -*-
"""Shared test cases."""

from django.test import TestCase
from shared.utils import force_as_list, sanitize_tag_label, BigIntConverter


class UtilsTests(TestCase):
    """Tests for shared.utils."""

    def test_force_as_list(self):
        self.assertEqual(force_as_list({}), [])
        self.assertEqual(force_as_list(None), [])
        self.assertEqual(force_as_list(1), [1])
        self.assertEqual(force_as_list([1]), [1])
        self.assertEqual(force_as_list([1, 2]), [1, 2])
        self.assertEqual(force_as_list([[1, 2]]), [1, 2])
        self.assertEqual(force_as_list([[1], 2]), [1, 2])

    def test_sanitize_tag_label(self):
        self.assertEqual(sanitize_tag_label("some-slug"), "SOMESLUG")

    def test_bigintconverter(self):
        con = BigIntConverter()
        self.assertTrue(isinstance(con.to_python('101'), int))
        self.assertTrue(isinstance(con.to_python('-101'), int))
        self.assertTrue(isinstance(con.to_url('101'), str))
        self.assertTrue(isinstance(con.to_url('-101'), str))
        self.assertRaises(ValueError, con.to_python, 'abc')
        self.assertRaises(ValueError, con.to_python, '-abc')
