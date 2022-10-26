"""
Page admin interface.
"""
from django.contrib import admin

from .models import Page, PageLink

admin.register(Page)
admin.register(PageLink)
