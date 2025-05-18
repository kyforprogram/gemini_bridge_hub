# backend/tasks.py
from celery import Celery
from python_to_translation import run_translation

# ← broker に加えて backend を指定
celery = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery.task(bind=True)
def translate_task(self, input_path, params):
    # run_translation 内で発生した例外はここでキャッチされ
    # AsyncResult に traceback とともに格納されます
    return run_translation(input_path, **params)

