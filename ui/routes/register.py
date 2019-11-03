import hashlib

from flask import Blueprint, redirect, render_template, request
from flask_login import current_user
from http import HTTPStatus

import config

from helpers import make_url, send_post
from log import get_logger
from schemas import validate_user


blueprint = Blueprint('register', __name__)
logger = get_logger()


@blueprint.route('/register', methods=['GET', 'POST'])
def route_register():
    logger.debug('current_user: %s', current_user)

    if current_user.is_authenticated:
        return redirect('/profile')

    variables = {
        'active_page': 'account'
    }

    if request.method == 'POST':
        status, message, data = validate_user(request.form)

        variables['status'] = status
        variables['message'] = message
        variables['data'] = data

        if status:
            data = {
                'email': request.form.get('email'),
                'password_hash': hashlib.sha256(request.form.get('password').encode('utf-8')).hexdigest()
            }

            response = send_post(make_url(config.API_URL, 'users'), json=data)

            if response.status_code == HTTPStatus.OK:
                variables['status'] = True
                variables['message'] = 'User registered'
            else:
                variables['status'] = False
                variables['message'] = 'Failed to register user'

    return render_template('register.html', **variables)
