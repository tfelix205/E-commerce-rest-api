import os 
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')


app = Celery('ecommerce_api')


# load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')


# auto-discover tasks in Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')