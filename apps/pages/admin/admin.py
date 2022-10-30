"""
Page admin interface.
"""
from django.contrib import admin

from apps.pages.models import Page, PageLink

admin.register(Page)
admin.register(PageLink)
