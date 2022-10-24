"""
Page model.
"""
from django.db import models


class BaseClass(models.Model):
    """
    Base audit class.
    """

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta class.
        """

        abstract = True


class Page(BaseClass):
    """
    Page database model.
    Used for storing page details.
    """

    processed_at = models.DateTimeField(null=True)
    url = models.URLField(max_length=500, unique=True, null=False)
    stats = models.JSONField(null=True)

    class Meta:
        """
        Meta class.
        """

        db_table = "pages"
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return f'URL: {self.url}'

    def __repr__(self) -> str:
        return f"Page: {self.url}"


class PageLink(BaseClass):
    """
    Page link database model.
    Used for storing page links.
    """

    href = models.CharField(max_length=255, null=False, blank=False)
    rel = models.CharField(max_length=255, null=True, blank=False)
    title = models.CharField(max_length=255, null=True, blank=False)
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )

    class Meta:
        """
        Meta class.
        """

        db_table = "pagelinks"
        verbose_name = "PageLink"
        verbose_name_plural = "PageLinks"

    def __str__(self):
        return f'URL: {self.href}'

    def __repr__(self) -> str:
        return f'Page Link: {self.url}'
