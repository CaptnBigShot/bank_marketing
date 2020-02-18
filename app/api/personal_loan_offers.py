from flask import jsonify, request, url_for, g, abort
from app import db
from app.models import PersonalLoanOffer
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/personal_loan_offers/<int:id>', methods=['PUT'])
@token_auth.login_required
def update(id):
    personal_loan_offer = PersonalLoanOffer.query.get_or_404(id)
    data = request.get_json() or {}
    if 'actual_response' not in data:
        return bad_request('must include actual_response field')
    personal_loan_offer.actual_response = data['actual_response']
    db.session.commit()
    return jsonify(id=personal_loan_offer.id, customer_id=personal_loan_offer.customer_id,
                   actual_response=personal_loan_offer.actual_response)
