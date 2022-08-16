


from flask_restful import Resource
from flask import render_template,Response,flash,redirect,url_for


class Home(Resource):
    def get(self):
        return "yay!"