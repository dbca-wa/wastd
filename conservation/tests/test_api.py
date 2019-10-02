# -*- coding: utf-8 -*-
"""Unit tests for Conservation module."""
from __future__ import unicode_literals

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase

from model_mommy import mommy  # noqa

from taxonomy.models import Taxon, Community
from conservation import models as cons_models

# Test updating taxon-conservationlisting with none, one, many cat and crit
# Test updating community-conservationlisting