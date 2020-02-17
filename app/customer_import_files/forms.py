from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import DataRequired


class CustomersForm(FlaskForm):
    customers_csv = FileField('Choose a file..', validators=[DataRequired()])
    submit = SubmitField('Upload CSV')
