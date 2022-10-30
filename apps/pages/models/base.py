"""
Base model.
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
