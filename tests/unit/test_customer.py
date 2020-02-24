import pytest
from app.models import Customer, PersonalLoanOffer


class TestCustomer:
    @pytest.mark.parametrize("code, description", {(1, 'Undergraduate'), (2, 'Graduate'), (3, 'Advanced/Professional')})
    def test_education_desc(self, code, description):
        customer = Customer(education=code)
        assert customer.education_desc() == description

    def test_to_dict(self):
        personal_loan_offer = PersonalLoanOffer(id=7, predicted_response='Accepted', prediction_probability=86.0,
                                                actual_response='No')
        customer = Customer(id=1, income=100, education=1, cc_avg=1.50, family=1, cd_account=False, age=40,
                            personal_loan_offer=personal_loan_offer)

        assert customer.to_dict() == {
            'age': 40,
            'cc_avg': '1.5',
            'cd_account': False,
            'education': 'Undergraduate',
            'family': 1,
            'id': 1,
            'income': 100,
            'personal_loan_offer_id': 7,
            'personal_loan_offer_prediction': 'Accepted',
            'personal_loan_offer_prediction_probability': '86.0',
            'personal_loan_offer_response': 'No',
        }
