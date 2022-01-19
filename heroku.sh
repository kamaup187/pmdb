#!/bin/bash
gunicorn wsgi:app --daemon
python worker.py