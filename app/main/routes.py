from app.main import bp
from flask import redirect, url_for, request, jsonify
from app import db
from flask_login import login_required
from app.models import Customer, PersonalLoanOffer


@bp.route("/")
@bp.route("/index")
@login_required
def index():
    return redirect(url_for('customer_import_files.index'))


@bp.route('/api/v1/delete_customer/<int:customer_id>', methods=["POST"])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'msg': 'Customer Deleted.'})


@bp.route('/api/v1/personal_loan_offer/<int:personal_loan_offer_id>', methods=["POST"])
def update_personal_loan_offer(personal_loan_offer_id):
    personal_loan_offer = PersonalLoanOffer.query.get(personal_loan_offer_id)
    actual_response = request.form['actual_response']
    personal_loan_offer.actual_response = actual_response
    db.session.commit()
    return jsonify(id=personal_loan_offer.id, customer_id=personal_loan_offer.customer_id,
                   actual_response=actual_response)
