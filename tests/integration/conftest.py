import pytest
import os
from config import Config, basedir
from app import create_app, db
from app.models import User


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    TEST_USERNAME = 'test'
    TEST_PASSWORD = 'test'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user(app):
    user = User(username=app.config['TEST_USERNAME'])
    user.set_password(app.config['TEST_PASSWORD'])
    db.session.add(user)
    db.session.commit()
    return user
