from celery import Celery
from python_to_translation import run_translation

celery = Celery('tasks', broker='redis://redis:6379/0')

@celery.task(bind=True)
def translate_task(self, input_path, params):
    return run_translation(input_path, **params)

