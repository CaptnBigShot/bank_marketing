import time
import base64
import os
import pandas as pd
from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from machine_learning.trained_models import PersonalLoanPredictionModel
from sqlalchemy import and_

personal_loan_prediction_model = PersonalLoanPredictionModel()


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

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp_local().strftime('%m/%d/%Y %I:%M %p'),
            'income': self.income,
            'education': self.education_desc(),
            'cc_avg': str(self.cc_avg),
            'family': self.family,
            'cd_account': self.cd_account,
            'age': self.age,
            'personal_loan_offer_id': self.personal_loan_offer.id,
            'personal_loan_offer_prediction': self.personal_loan_offer.predicted_response,
            'personal_loan_offer_prediction_probability': str(self.personal_loan_offer.prediction_probability),
            'personal_loan_offer_response': self.personal_loan_offer.actual_response,
        }


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

    def personal_loan_offers(self):
        offers = PersonalLoanOffer.query.filter(and_(
            Customer.import_file == self,
            PersonalLoanOffer.customer_id == Customer.id,
        ))
        return offers

    def personal_loan_offers_to_be_accepted(self):
        offers = PersonalLoanOffer.query.filter(and_(
            Customer.import_file == self,
            PersonalLoanOffer.customer_id == Customer.id,
            PersonalLoanOffer.predicted_response == 'Accepted',
        ))
        return offers

    def count_predicted_to_accept_personal_loan(self):
        return self.personal_loan_offers_to_be_accepted().count()

    def response_counts_for_personal_loan_offers_to_be_accepted(self):
        offers = self.personal_loan_offers_to_be_accepted()
        accepted, declined, no_response = 0, 0, 0

        for p in offers:
            if p.actual_response == 'Accepted':
                accepted += 1
            elif p.actual_response == 'Declined':
                declined += 1
            else:
                no_response += 1

        return accepted, declined, no_response

    def personal_loan_offers_with_response(self):
        offers = self.personal_loan_offers()
        offers_with_response = [p for p in offers if p.actual_response != ""]
        percent_with_response = round(((float(len(offers_with_response)) / float(offers.count())) * 100), 2)
        return percent_with_response

    @staticmethod
    def process_customer_import_file(file_path, process_actual_responses=False):
        # Read the file
        df = pd.read_csv(file_path, delimiter='\t', header=0)

        # Run predictions on customers
        features = ['Income', 'Education', 'CCAvg', 'Family', 'CDAccount', 'Age']
        df_predicted = personal_loan_prediction_model.predict_customer_responses(df[features].copy())

        # Include the actual responses if specified (do this AFTER running predictions)
        if process_actual_responses:
            df_predicted.loc[:, 'ActualResponse'] = df['PersonalLoan'].apply(lambda x: "Accepted" if x == 1 else "Declined")
        else:
            df_predicted['ActualResponse'] = ""

        # Create file in DB
        file_name = os.path.basename(file_path)
        import_file = CustomerImportFile(name=file_name)
        db.session.add(import_file)

        # Load each customer & prediction into the DB
        for idx, row in df_predicted.iterrows():
            # Customer
            income = int(row['Income'])
            education = int(row['Education'])
            cc_avg = float(row['CCAvg'])
            family = int(row['Family'])
            cd_account = bool(row['CDAccount'])
            age = int(row['Age'])
            customer = Customer(income=income, education=education,
                                cc_avg=cc_avg, family=family,
                                cd_account=cd_account, age=age,
                                import_file=import_file)
            db.session.add(customer)

            # Personal Loan Offer
            predicted_response = 'Accepted' if row['Prediction'] == 1 else 'Declined'
            prediction_probability = float(row['PredictionProbability']) * 100
            actual_response = row['ActualResponse']
            personal_loan_offer = PersonalLoanOffer(customer=customer,
                                                    predicted_response=predicted_response,
                                                    prediction_probability=prediction_probability,
                                                    actual_response=actual_response)
            db.session.add(personal_loan_offer)

        return import_file


class PersonalLoanOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    predicted_response = db.Column(db.String(15))
    prediction_probability = db.Column(db.Numeric(10, 2))
    actual_response = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<PersonalLoanOffer {} {}>'.format(self.id, self.customer_id)

    @staticmethod
    def prediction_accuracy_counts():
        accurate = PersonalLoanOffer.query.filter(and_(
            PersonalLoanOffer.actual_response != '',
            PersonalLoanOffer.actual_response == PersonalLoanOffer.predicted_response
        )).count()

        inaccurate = PersonalLoanOffer.query.filter(and_(
            PersonalLoanOffer.actual_response != '',
            PersonalLoanOffer.actual_response != PersonalLoanOffer.predicted_response
        )).count()

        return accurate, inaccurate

    @staticmethod
    def prediction_counts_for_accepted_offers():
        pred_to_accept = PersonalLoanOffer.query.filter(and_(
            PersonalLoanOffer.actual_response == 'Accepted',
            PersonalLoanOffer.predicted_response == 'Accepted'
        )).count()

        pred_to_decline = PersonalLoanOffer.query.filter(and_(
            PersonalLoanOffer.actual_response == 'Accepted',
            PersonalLoanOffer.predicted_response == 'Declined'
        )).count()

        return pred_to_accept, pred_to_decline

    @staticmethod
    def probability_line_chart_data():
        line_chart_data = {'labels': [], 'data': []}
        min_prob = 92
        low_prob_count = PersonalLoanOffer.query.filter(PersonalLoanOffer.prediction_probability < min_prob).count()
        line_chart_data['labels'].append("< " + str(min_prob))
        line_chart_data['data'].append(low_prob_count)

        for i in range(min_prob, 101, 2):
            percent = float(i)
            count = PersonalLoanOffer.query.filter_by(prediction_probability=percent).count()
            line_chart_data['labels'].append(str(i))
            line_chart_data['data'].append(count)

        return line_chart_data
