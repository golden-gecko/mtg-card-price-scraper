from flask import Blueprint, render_template


blueprint = Blueprint('contact', __name__)


@blueprint.route('/contact')
def route_contact():
    return render_template('contact.html', active_page='contact')
