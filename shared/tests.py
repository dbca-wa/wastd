# -*- coding: utf-8 -*-
"""Shared test cases."""
from __future__ import unicode_literals

from django.test import TestCase
# from django.urls import reverse
# from config.urls import urlpatterns

from shared.utils import (force_as_list, sanitize_tag_label)

# class UrlsTest(TestCase):
#     """Test all URLs."""

#     def test_responses(self):
#         """Test that all URLs load with status 200."""
#         for url in urlpatterns:
#             response = self.client.get(reverse(url.name))
#             self.assertEqual(response.status_code, 200)

class UtilsTests(TestCase):
	"""Tests for shared.utils."""

	def test_force_as_list(self):
		self.assertEqual(force_as_list({}), [])
		self.assertEqual(force_as_list(None), [])
		self.assertEqual(force_as_list(1), [1])
		self.assertEqual(force_as_list([1]), [1])
		self.assertEqual(force_as_list([1,2]), [1,2])
		self.assertEqual(force_as_list([[1, 2]]), [1,2])
		self.assertEqual(force_as_list([[1], 2]), [1,2])

	def test_sanitize_tag_label(self):
		self.assertEqual(sanitize_tag_label("some-slug"), "SOMESLUG")