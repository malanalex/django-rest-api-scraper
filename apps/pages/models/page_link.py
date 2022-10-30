"""
PageLink model.
"""
from django.db import models

from .base import BaseClass
from .page import Page


class PageLink(BaseClass):
    """
    Page link database model.
    Used for storing page links.
    """

    href = models.CharField(max_length=600, null=False, blank=False)
    rel = models.CharField(max_length=600, null=True, blank=False)
    title = models.CharField(max_length=600, null=True, blank=False)
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="links",
    )

    class Meta:
        """
        Meta class.
        """

        db_table = "pagelinks"
        verbose_name = "PageLink"
        verbose_name_plural = "PageLinks"

    def __str__(self):
        return f"URL: {self.href}"

    def __repr__(self) -> str:
        return f"Page Link: {self.url}"
