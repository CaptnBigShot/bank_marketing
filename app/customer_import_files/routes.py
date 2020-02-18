import os
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import current_app, db
from app.customer_import_files.forms import CustomersForm
from app.models import Customer, CustomerImportFile, PersonalLoanOffer
from app.customer_import_files import bp
from app.api.tokens import get_token_for_user


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = CustomersForm()
    if form.validate_on_submit():
        if form.customers_csv.data:
            # Save the file
            file_path = form.save_file(current_app.config['UPLOAD_FOLDER'])

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
    jupyter_url = current_app.config['PERSONAL_LOAN_OFFERS_JUPYTER_URL']

    # Get bar chart data
    (pred_to_accept, pred_to_decline) = PersonalLoanOffer.prediction_counts_for_accepted_offers()
    bar_chart_data = [pred_to_accept, pred_to_decline]

    # Get pie chart data
    (accurate, inaccurate) = PersonalLoanOffer.prediction_accuracy_counts()
    accuracy_pie_data = [accurate, inaccurate]

    # Get line chart data
    line_chart_data = PersonalLoanOffer.probability_line_chart_data()

    return render_template('customer_import_files/index.html', title='Dashboard', form=form,
                           import_files=import_files,
                           customers=customers,
                           jupyter_url=jupyter_url,
                           bar_chart_data=bar_chart_data,
                           accuracy_pie_data=accuracy_pie_data,
                           line_chart_data=line_chart_data)


@bp.route('/<int:id>', methods=['GET'])
@login_required
def show(id):
    customer_import_file = CustomerImportFile.query.get_or_404(id)
    customers = [c.to_dict() for c in customer_import_file.customers]

    # Get bar chart data
    (accepted, declined, no_response) = customer_import_file.response_counts_for_personal_loan_offers_to_be_accepted()
    bar_chart_data = [accepted, declined, no_response]

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
