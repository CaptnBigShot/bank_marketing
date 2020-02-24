import pytest
from app import db
from app.models import Customer


class TestCustomersApi:
    @pytest.fixture
    def customer(self, app):
        customer = Customer(income=100, education=1, cc_avg=1.50, family=1, cd_account=False, age=40)
        db.session.add(customer)
        db.session.commit()
        return customer

    def test_delete(self, app, user, customer):
        with app.test_client() as client:
            response = client.delete("/api/customers/1", headers={"Authorization": 'Bearer ' + user.get_token()})
            data = response.get_json()
            assert response.status_code == 200
            assert data == {'message': 'Customer Deleted.'}
            assert Customer.query.all() == []

    def test_delete_a_non_existing_customer(self, app, user, customer):
        with app.test_client() as client:
            response = client.delete("/api/customers/2", headers={"Authorization": 'Bearer ' + user.get_token()})
            data = response.get_json()
            assert response.status_code == 404
            assert data == {'error': 'Not Found'}
            assert Customer.query.all() == [customer]

    def test_delete_as_unauthorized_user(self, app, customer):
        with app.test_client() as client:
            response = client.delete("/api/customers/2", headers={"Authorization": 'Bearer ' + "X"})
            data = response.get_json()
            assert response.status_code == 401
            assert data == {'error': 'Unauthorized'}
            assert Customer.query.all() == [customer]
