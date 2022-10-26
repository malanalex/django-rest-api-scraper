"""
Celery main module.
"""
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

import core

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("cel_app")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
