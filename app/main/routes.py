from app.main import bp
from flask import redirect, url_for
from flask_login import login_required


@bp.route("/")
@bp.route("/index")
@login_required
def index():
    return redirect(url_for('customer_import_files.index'))
