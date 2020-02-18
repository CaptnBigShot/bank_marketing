from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import customers, personal_loan_offers, errors, tokens
