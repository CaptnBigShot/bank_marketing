import pytest
from app import db
from app.models import Customer, PersonalLoanOffer


class TestPersonalLoanOffersApi:
    @pytest.fixture
    def personal_loan_offer(self, app):
        customer = Customer(income=100, education=1, cc_avg=1.50, family=1, cd_account=False, age=40)
        personal_loan_offer = PersonalLoanOffer(predicted_response='Accepted', prediction_probability=96.0,
                                                actual_response='', customer=customer)
        db.session.add(personal_loan_offer)
        db.session.commit()
        return personal_loan_offer

    def test_update(self, app, user, personal_loan_offer):
        with app.test_client() as client:
            response = client.put("/api/personal_loan_offers/1",
                                  headers={"Authorization": 'Bearer ' + user.get_token()},
                                  json={'actual_response': 'Declined'})
            data = response.get_json()
            assert response.status_code == 200
            assert data == {'actual_response': 'Declined', 'customer_id': 1, 'id': 1}
            assert personal_loan_offer.actual_response == 'Declined'

    def test_update_without_payload(self, app, user, personal_loan_offer):
        with app.test_client() as client:
            response = client.put("/api/personal_loan_offers/1",
                                  headers={"Authorization": 'Bearer ' + user.get_token()})
            data = response.get_json()
            assert response.status_code == 400
            assert data == {'error': 'Bad Request', 'message': 'must include actual_response field'}
            assert personal_loan_offer.actual_response == ''

    def test_update_as_unauthorized_user(self, app, personal_loan_offer):
        with app.test_client() as client:
            response = client.put("/api/personal_loan_offers/1",
                                  headers={"Authorization": 'Bearer ' + 'X'},
                                  json={'actual_response': 'Declined'})
            data = response.get_json()
            assert response.status_code == 401
            assert data == {'error': 'Unauthorized'}
            assert personal_loan_offer.actual_response == ''
