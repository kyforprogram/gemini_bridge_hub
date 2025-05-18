#!/bin/sh
celery -A tasks worker --loglevel=info

