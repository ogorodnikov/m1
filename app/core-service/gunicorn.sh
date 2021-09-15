#!/bin/sh

# gunicorn run:app --config="python:core.gunicorn.config"

gunicorn run:app --reload