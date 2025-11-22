from flask import Blueprint, render_template

from log import get_logger


blueprint = Blueprint('index', __name__)
logger = get_logger()


@blueprint.route('/')
def route_index():
    return render_template('index.html', active_page='home')
