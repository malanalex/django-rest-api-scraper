"""
Failed task model.
"""
import importlib
import json

from django.db import models

from .base import BaseClass


class FailedTask(BaseClass):
    """
    Failed task model.
    Used for storing failed task details.
    """

    updated_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=125)
    full_name = models.TextField()
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    exception_class = models.TextField()
    exception_msg = models.TextField()
    traceback = models.TextField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=36)
    failures = models.PositiveSmallIntegerField(default=1)

    class Meta:
        """
        Meta class.
        """

        ordering = ("-updated_at",)

    def retry_and_delete(self, inline=False):
        """
        Retry the task and delete the failed task record.

        :param inline: If True, the task will be executed inline.
        """
        mod_name, func_name = self.full_name.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)

        args = json.loads(self.args) if self.args else ()
        kwargs = json.loads(self.kwargs) if self.kwargs else {}
        if inline:
            try:
                res = func(*args, **kwargs)
                self.delete()
                return res
            except Exception as e:
                raise e

        self.delete()
        return func.delay(*args, **kwargs)
