import pytest
from app.models import Customer, CustomerImportFile, PersonalLoanOffer
from datetime import datetime


class TestCustomerImportFile:
    def test_customers_count(self):
        import_file = CustomerImportFile()
        assert import_file.customers_count() == 0

        Customer(import_file=import_file)
        assert import_file.customers_count() == 1
