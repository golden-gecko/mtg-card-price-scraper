from flask import Blueprint, render_template
from flask_login import login_required


blueprint = Blueprint('profile', __name__)


@blueprint.route('/profile')
@login_required
def route_profile():
    return render_template('profile.html', active_page='profile')
