from app import create_app, db
from app.models import User, Customer, PersonalLoanOffer, CustomerImportFile

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Customer': Customer,
        'PersonalLoanOffer': PersonalLoanOffer,
        'CustomerImportFile': CustomerImportFile
    }
