import os
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import current_app, db
from app.customer_import_files.forms import CustomersForm
from app.models import Customer, CustomerImportFile, PersonalLoanOffer
from app.customer_import_files import bp
from machine_learning.trained_models import PersonalLoanPredictionModel
from app.api.tokens import get_token_for_user

personal_loan_prediction_model = PersonalLoanPredictionModel()


def personal_loan_offers_bar_chart_data(personal_loan_offers):
    data = {
        'accepted_predicted_to_accept': 0,
        'accepted_predicted_to_decline': 0,
        'declined_predicted_to_accept': 0,
        'declined_predicted_to_decline': 0,
        'no_response_predicted_to_accept': 0,
        'no_response_predicted_to_decline': 0,
    }

    for p in personal_loan_offers:
        actual_response = p.actual_response
        predicted_response = p.predicted_response

        if actual_response == 'Accepted' and predicted_response == 'Accepted':
            data['accepted_predicted_to_accept'] += 1

        if actual_response == 'Accepted' and predicted_response == 'Declined':
            data['accepted_predicted_to_decline'] += 1

        if actual_response == 'Declined' and predicted_response == 'Accepted':
            data['declined_predicted_to_accept'] += 1

        if actual_response == 'Declined' and predicted_response == 'Declined':
            data['declined_predicted_to_decline'] += 1

        if actual_response == '' and predicted_response == 'Accepted':
            data['no_response_predicted_to_accept'] += 1

        if actual_response == '' and predicted_response == 'Declined':
            data['no_response_predicted_to_decline'] += 1

    return data


def personal_loan_offers_probability_line_chart_data():
    line_chart_data = {'labels': [], 'data': []}
    min_prob = 92
    low_prob_count = PersonalLoanOffer.query.filter(PersonalLoanOffer.prediction_probability < min_prob).count()
    line_chart_data['labels'].append("< " + str(min_prob))
    line_chart_data['data'].append(low_prob_count)

    for i in range(min_prob, 101, 2):
        percent = float(i)
        count = PersonalLoanOffer.query.filter_by(prediction_probability=percent).count()
        line_chart_data['labels'].append(str(i))
        line_chart_data['data'].append(count)

    return line_chart_data


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = CustomersForm()
    if form.validate_on_submit():
        if form.customers_csv.data:
            # Save the file
            file_name = secure_filename(form.customers_csv.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
            form.customers_csv.data.save(file_path)

            # Process the file into the DB
            import_file = CustomerImportFile.process_customer_import_file(file_path)

            # Save changes to DB
            db.session.commit()

            # Delete the uploaded file
            os.remove(file_path)

        flash('Customers have been uploaded.')
        return redirect(url_for('customer_import_files.show', id=import_file.id))

    import_files = CustomerImportFile.query.all()
    customers = Customer.query.all()

    # Get bar chart data
    customer_personal_loan_offers = [c.personal_loan_offer for c in customers]
    bar_chart_data = personal_loan_offers_bar_chart_data(customer_personal_loan_offers)

    # Get pie chart data
    accurate_preds = bar_chart_data['accepted_predicted_to_accept'] + bar_chart_data['declined_predicted_to_decline']
    inaccurate_preds = bar_chart_data['accepted_predicted_to_decline'] + bar_chart_data['declined_predicted_to_accept']
    accuracy_pie_data = [accurate_preds, inaccurate_preds]

    # Get line chart data
    line_chart_data = personal_loan_offers_probability_line_chart_data()

    return render_template('customer_import_files/index.html', title='Home', form=form, import_files=import_files,
                           customers=customers,
                           jupyter_url=current_app.config['PERSONAL_LOAN_OFFERS_JUPYTER_URL'],
                           bar_chart_data=bar_chart_data,
                           accuracy_pie_data=accuracy_pie_data,
                           line_chart_data=line_chart_data)


@bp.route('/<int:id>', methods=['GET'])
@login_required
def show(id):
    customer_import_file = CustomerImportFile.query.get(id)
    customers = [c.to_dict() for c in customer_import_file.customers]

    # Get bar chart data
    personal_loan_offers = customer_import_file.customer_personal_loan_offers()
    bar_chart_data = personal_loan_offers_bar_chart_data(personal_loan_offers)

    # Get API token for ajax requests
    user_auth_token = get_token_for_user(current_user)

    return render_template('customer_import_files/show.html', title='Customer Import File',
                           customer_import_file=customer_import_file,
                           customers=customers,
                           user_auth_token=user_auth_token,
                           bar_chart_data=bar_chart_data)


@bp.route("/delete/<int:id>")
@login_required
def delete(id):
    import_file = CustomerImportFile.query.get_or_404(id)
    db.session.delete(import_file)
    db.session.commit()
    flash('Deleted customer import file.')
    return redirect(url_for('customer_import_files.index'))
