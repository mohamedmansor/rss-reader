import os

from celery import Celery
from django.conf import settings

from .celery_beat import setup_periodic_tasks

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("rrs_reader")
setup_periodic_tasks(app)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if hasattr(settings, "SCOUT_KEY"):
    import scout_apm.celery
    from scout_apm.api import Config

    Config.set(
        key=settings.SCOUT_KEY,
        name=settings.SCOUT_NAME,
        monitor=settings.SCOUT_MONITOR,
    )

    scout_apm.celery.install(app)
