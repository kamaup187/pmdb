import os

from .secrets import *
from flask_restful import Resource
from flask import render_template,Response,flash,redirect,url_for

from .decor import lfile


class Home(Resource):
    def get(self):
        text_to_print = os.getenv("JEJEJ") or jeje
        # os.environ.get('CLOUDINARY_URL') or
        lfile(text_to_print)
        lfile("second one")
        return "yay!"

# class Tee(object):
#     def __init__(self, *files):
#         self.files = files
#     def write(self, obj):
#         for f in self.files:
#             f.write(obj)

#     def flush(self):
#         pass


# f = open('logfile', 'w')
# backup = sys.stdout
# sys.stdout = Tee(sys.stdout, f)