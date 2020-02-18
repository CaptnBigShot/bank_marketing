from flask_seeder import Seeder
from app import db
from app.models import CustomerImportFile
import config
import os


class CustomerImportFileSeeder(Seeder):
    def __init__(self):
        super().__init__(db=db)
        self.priority = 20

    def run(self):
        training_data_file_path = os.path.join(config.basedir, 'machine_learning', 'personal_loan_data.csv')
        CustomerImportFile.process_customer_import_file(training_data_file_path, process_actual_responses=True)
