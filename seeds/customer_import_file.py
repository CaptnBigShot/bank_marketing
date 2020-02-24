import os
import config
import pandas as pd
from flask_seeder import Seeder
from app import db
from app.models import CustomerImportFile


class CustomerImportFileSeeder(Seeder):
    def __init__(self):
        super().__init__(db=db)
        self.priority = 20

    def run(self):
        file_name = 'personal_loan_data.csv'
        file_path = os.path.join(config.basedir, 'machine_learning', file_name)
        df = pd.read_csv(file_path, delimiter='\t', header=0)
        import_file = CustomerImportFile.process_customer_import_file(df, file_name, True)
        db.session.add(import_file)
