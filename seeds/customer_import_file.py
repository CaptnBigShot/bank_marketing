from flask_seeder import Seeder
from app import db
from app.models import CustomerImportFile, Customer, PersonalLoanOffer
from machine_learning.trained_models import PersonalLoanPredictionModel
import pandas as pd
import config
import os


class CustomerImportFileSeeder(Seeder):
    def __init__(self):
        super().__init__(db=db)
        self.priority = 20

    def run(self):
        training_data_file = os.path.join(config.basedir, 'machine_learning', 'personal_loan_data.csv')

        # Read the file
        df = pd.read_csv(training_data_file, delimiter='\t', header=0)

        # Load the prediction model
        personal_loan_prediction_model = PersonalLoanPredictionModel()

        # Run predictions on customers
        features = ['Income', 'Education', 'CCAvg', 'Family', 'CDAccount', 'Age']
        target = df['PersonalLoan']
        df = personal_loan_prediction_model.predict_customer_responses(df[features].copy())
        df['PersonalLoan'] = target

        # Create file in DB
        import_file = CustomerImportFile(name="initial_data.csv")
        db.session.add(import_file)

        # Load each customer & prediction into the DB
        for idx, row in df.iterrows():
            # Customer
            income = int(row['Income'])
            education = int(row['Education'])
            cc_avg = float(row['CCAvg'])
            family = int(row['Family'])
            cd_account = bool(row['CDAccount'])
            age = int(row['Age'])
            customer = Customer(income=income, education=education,
                                cc_avg=cc_avg, family=family,
                                cd_account=cd_account, age=age, import_file=import_file)
            db.session.add(customer)

            # Personal Loan Offer Prediction
            actual_response = 'Accepted' if row['PersonalLoan'] == 1 else 'Declined'
            predicted_response = 'Accepted' if row['Prediction'] == 1 else 'Declined'
            prediction_probability = float(row['PredictionProbability']) * 100
            personal_loan_offer = PersonalLoanOffer(customer=customer, predicted_response=predicted_response,
                                                    prediction_probability=prediction_probability,
                                                    actual_response=actual_response)
            db.session.add(personal_loan_offer)

        # Save changes to DB
        db.session.commit()
