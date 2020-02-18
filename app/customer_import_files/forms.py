import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import DataRequired


class CustomersForm(FlaskForm):
    customers_csv = FileField('Choose a file..', validators=[DataRequired()])
    submit = SubmitField('Upload CSV')

    def save_file(self, file_directory):
        file_name = secure_filename(self.customers_csv.data.filename)
        file_path = os.path.join(file_directory, file_name)
        self.customers_csv.data.save(file_path)
        return file_path
