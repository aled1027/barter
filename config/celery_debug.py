import os

import structlog
from celery import Celery
from django.http import HttpResponse

from config.tasks import _debug_task

logger = structlog.get_logger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


def debug(req) -> HttpResponse:
    result = _debug_task.delay()
    # If the task is healthy, return a 200
    if result.status in ["PENDING", "STARTED", "SUCCESS"]:
        return HttpResponse("Debug task sent", status=200)
    return HttpResponse(f"Debug task failed: {result.status}", status=500)
