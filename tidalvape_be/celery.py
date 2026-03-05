import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tidalvape_be.settings")

app = Celery("tidalvape_be")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()