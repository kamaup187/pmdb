#!/bin/bash
gunicorn wsgi:app --daemon
python worker.py
python clock.py