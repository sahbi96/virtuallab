from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
import requests
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
app = Celery('Backend',backend="db+sqlite:///db.sqlite3")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def update_models(arg):
    url1 = os.getenv('API_SKILLS_UPDATE', default="http://127.0.0.1:7200/predict_to_user/")
    r2= requests.post(url1,json={})

    url2 = os.getenv('API_RECOMMENDED_UPDATE', default="http://127.0.0.1:7200/predict_to_user/")
    r2= requests.post(url2,json={})
    return True


@app.on_after_configure.connect
def update_model_periodic(**kwargs):
    app.add_periodic_task(3600.0, update_models.s(''), name='add every hour')