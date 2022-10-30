"""
Celery tasks module.
"""
import json

from celery import Task
from django.utils import timezone

from apps.pages.models import FailedTask


class LogErrorsTask(Task):
    """
    Base exception log class for tasks.
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.save_failed_task(exc, task_id, args, kwargs, einfo)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def save_failed_task(self, exc, task_id, args, kwargs, traceback):
        """
        :type exc: Exception
        """
        task = FailedTask()
        task.celery_task_id = task_id
        task.full_name = self.name
        task.name = self.name.split(".")[-1]
        task.exception_class = exc.__class__.__name__
        task.exception_msg = str(exc)
        task.traceback = traceback
        task.updated_at = timezone.now()

        if args:
            task.args = json.dumps(list(args))
        if kwargs:
            task.kwargs = json.dumps(kwargs)

        # Find if task with same args, name and exception already exists
        # If it do, update failures count and last updated_at
        existing_task = FailedTask.objects.filter(
            args=task.args,
            kwargs=task.kwargs,
            full_name=task.full_name,
            exception_class=task.exception_class,
        )

        if len(existing_task):
            existing_task = existing_task[0]
            existing_task.failures += 1
            existing_task.updated_at = task.updated_at
            existing_task.save(
                force_update=True, update_fields=("updated_at", "failures")
            )
        else:
            task.save(force_insert=True)
