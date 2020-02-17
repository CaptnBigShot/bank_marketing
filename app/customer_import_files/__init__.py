from flask import Blueprint

bp = Blueprint('customer_import_files', __name__)

from app.customer_import_files import routes
