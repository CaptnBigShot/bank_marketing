from flask import jsonify, request, url_for, g, abort
from app import db
from app.models import Customer
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/customers/<int:id>', methods=['GET'])
@token_auth.login_required
def get_customer(id):
    return jsonify({'age': Customer.query.get_or_404(id).age})


@bp.route('/customers/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer Deleted.'})
