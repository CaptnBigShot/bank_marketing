import pytest
import pandas as pd
from app.models import Customer, CustomerImportFile


class TestCustomerImportFile:
    def test_customers_count(self):
        import_file = CustomerImportFile()
        assert import_file.customers_count() == 0

        Customer(import_file=import_file)
        assert import_file.customers_count() == 1

    @pytest.mark.parametrize("process_actual_responses", {True, False})
    def test_process_customer_import_file(self, process_actual_responses):
        df_customers = {
            'Income': [183, 39],
            'Education': [3, 2],
            'CCAvg': [6.90, 2.40],
            'Family': [2, 3],
            'CDAccount': [1, 0],
            'Age': [30, 61],
            'PersonalLoan': [1, 0]
        }
        df_columns = ['Income', 'Education', 'CCAvg', 'Family', 'CDAccount', 'Age', 'PersonalLoan']
        df = pd.DataFrame(df_customers, columns=df_columns)

        # Process the data frame
        file_name = 'test.csv'
        import_file = CustomerImportFile.process_customer_import_file(df, file_name, process_actual_responses)
        assert import_file.name == file_name

        # Compare processed customer and personal loan offers against expected results
        import_file_customers_dicts = [c.to_dict() for c in import_file.customers]
        expected_customers_dicts = [
            {
                'id': None,
                'income': 183,
                'education': 'Advanced/Professional',
                'cc_avg': '6.9',
                'family': 2,
                'cd_account': True,
                'age': 30,
                'personal_loan_offer_id': None,
                'personal_loan_offer_prediction': 'Accepted',
                'personal_loan_offer_prediction_probability': '92.0',
                'personal_loan_offer_response': '' if not process_actual_responses else 'Accepted'
            },
            {
                'id': None,
                'income': 39,
                'education': 'Graduate',
                'cc_avg': '2.4',
                'family': 3,
                'cd_account': False,
                'age': 61,
                'personal_loan_offer_id': None,
                'personal_loan_offer_prediction': 'Declined',
                'personal_loan_offer_prediction_probability': '100.0',
                'personal_loan_offer_response': '' if not process_actual_responses else 'Declined'
            }
        ]

        assert import_file_customers_dicts == expected_customers_dicts
