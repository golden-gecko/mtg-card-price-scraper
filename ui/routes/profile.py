from flask import render_template
from flask_login import login_required

from app import app


@app.route('/profile')
@login_required
def route_profile():
    return render_template('profile.html', active_page='profile')
