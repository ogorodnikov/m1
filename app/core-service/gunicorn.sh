#!/bin/sh
gunicorn run:app --bind 0.0.0.0:8080 --reload --timeout 900
