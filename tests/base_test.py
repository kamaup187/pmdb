
from flask_testing import TestCase
from flask_login import login_user,logout_user

from app import create_app, db


class BaseTest(TestCase):

    # SQLALCHEMY_DATABASE_URI = "sqlite://"
    # TESTING = True

    def create_app(self):

        # pass in test configuration
        return create_app("testing")

    def setUp(self):

        db.create_all()

    def tearDown(self):
        logout_user()
        db.session.remove()
        db.session.close()

        db.drop_all()









