from celery import shared_task


@shared_task
def _debug_task():
    """A dummy task for testing Celery."""
    pass