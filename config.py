import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SF83FSKFLSFPQWYXNZMVHF729'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERSONAL_LOAN_OFFERS_JUPYTER_URL = 'https://mybinder.org/v2/gh/CaptnBigShot/bank_marketing/master?filepath=machine_learning%2Fjupyter_personal_loan.ipynb'
    UPLOAD_FOLDER = 'uploads'
    BOOTSTRAP_SERVE_LOCAL = True
