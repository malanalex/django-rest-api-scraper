"""
Page model.
"""
from django.db import models

from .base import BaseClass


class Page(BaseClass):
    """
    Page database model.
    Used for storing page details.
    """

    processed_at = models.DateTimeField(null=True)
    url = models.URLField(max_length=600, unique=True, null=False)
    stats = models.JSONField(null=True)

    class Meta:
        """
        Meta class.
        """

        db_table = "pages"
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return f"URL: {self.url}"

    def __repr__(self) -> str:
        return f"Page: {self.url}"
