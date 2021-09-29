#!/bin/sh
# gunicorn run:app --bind 0.0.0.0:8080 --reload --timeout 900

# gunicorn --bind 0.0.0.0:8080 run:app --reload --workers 1 --access-logfile '-' --log-level 'debug' --access_log_format '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# gunicorn run:app

gunicorn run:app --reload