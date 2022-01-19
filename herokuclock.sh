#!/bin/bash
gunicorn wsgi:app --daemon
python clock.py