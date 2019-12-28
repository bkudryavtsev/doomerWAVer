#!/usr/bin/env sh

/home/ubuntu/.local/bin/uwsgi --plugin python3 --http :80 --wsgi-file doomerwaver.py
