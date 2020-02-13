from datetime import datetime
import time
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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


class PersonalLoanOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    predicted_response = db.Column(db.String(15))
    prediction_probability = db.Column(db.Numeric(10, 2))
    actual_response = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<PersonalLoanOffer {} {}>'.format(self.id, self.customer_id)
