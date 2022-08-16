from flask_restful import Api
from flask import Blueprint

from .views.nano import *


version_one = Blueprint('api', __name__)
api = Api(version_one)

api.add_resource(Home,"/home")