import time
import base64
import os
from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def utc_to_local(utc_timestamp):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_timestamp + offset


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    income = db.Column(db.Integer)
    education = db.Column(db.Integer)
    cc_avg = db.Column(db.Numeric(10, 2))
    family = db.Column(db.Integer)
    cd_account = db.Column(db.Boolean)
    age = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    personal_loan_offer = db.relationship('PersonalLoanOffer', uselist=False, backref='customer', cascade="all,delete")
    import_file_id = db.Column(db.Integer, db.ForeignKey('customer_import_file.id'))
    import_file = db.relationship("CustomerImportFile", back_populates="customers")

    def __repr__(self):
        return '<Customer {} {} {}>'.format(self.id, self.age, self.income)

    def education_desc(self):
        if self.education == 1:
            return 'Undergraduate'
        elif self.education == 2:
            return 'Graduate'
        elif self.education == 3:
            return 'Advanced/Professional'
        else:
            return self.education

    def timestamp_local(self):
        return utc_to_local(self.timestamp)

    @staticmethod
    def customers_to_json(customers):
        customers_json = []
        for c in customers:
            customer_json = {
                'id': c.id,
                'timestamp': c.timestamp_local().strftime('%m/%d/%Y %I:%M %p'),
                'income': c.income,
                'education': c.education_desc(),
                'cc_avg': str(c.cc_avg),
                'family': c.family,
                'cd_account': c.cd_account,
                'age': c.age,
                'personal_loan_offer_id': c.personal_loan_offer.id,
                'personal_loan_offer_prediction': c.personal_loan_offer.predicted_response,
                'personal_loan_offer_prediction_probability': str(c.personal_loan_offer.prediction_probability),
                'personal_loan_offer_response': c.personal_loan_offer.actual_response,
            }
            customers_json.append(customer_json)
        return customers_json


class CustomerImportFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    customers = db.relationship("Customer", back_populates="import_file", cascade="all,delete")

    def __repr__(self):
        return '<CustomerImportFile {} {} {}>'.format(self.id, self.name, self.timestamp)

    def timestamp_local(self):
        return utc_to_local(self.timestamp)

    def customers_count(self):
        return len(self.customers)

    def customer_personal_loan_offers(self):
        return [c.personal_loan_offer for c in self.customers]

    def count_predicted_to_accept_personal_loan(self):
        pred_to_accept = [p for p in self.customer_personal_loan_offers() if p.predicted_response == 'Accepted']
        return len(pred_to_accept)

    def personal_loan_offer_prediction_accuracy(self):
        offers = self.customer_personal_loan_offers()
        accurate_predictions = [p for p in offers if p.predicted_response == p.actual_response]
        accuracy = round(((float(len(accurate_predictions)) / float(len(offers))) * 100), 2)
        return accuracy

    def personal_loan_offers_with_response(self):
        offers = self.customer_personal_loan_offers()
        offers_with_response = [p for p in offers if p.actual_response != ""]
        percent_with_response = round(((float(len(offers_with_response)) / float(len(offers))) * 100), 2)
        return percent_with_response


class PersonalLoanOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    predicted_response = db.Column(db.String(15))
    prediction_probability = db.Column(db.Numeric(10, 2))
    actual_response = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<PersonalLoanOffer {} {}>'.format(self.id, self.customer_id)
