import hashlib
import http

from flask import make_response, redirect, render_template, request
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urljoin

import config

from app import app, User
from helpers import send_post
from log import get_logger
from schemas import validate_user


logger = get_logger()


@app.route('/login', methods=['GET', 'POST'])
def route_login():
    logger.debug('current_user: %s', current_user)

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

            api_response = send_post(urljoin(config.API_URL, 'auth'), json=data)

            if api_response.status_code == http.HTTPStatus.OK:
                variables['status'] = True
                variables['message'] = 'User authorized'

                response = make_response(render_template('auth.html', **variables))
                response.set_cookie('jwt', api_response.json()['data']['access_token'])

                login_user(User(api_response.json()['data']['access_token']))

                return response
            else:
                variables['status'] = False
                variables['message'] = 'Failed to authorize user'

    return render_template('auth.html', **variables)


@app.route('/logout')
@login_required
def route_logout():
    logger.debug('current_user: %s', current_user)

    headers = {
        'Authorization': 'Bearer {}'.format(current_user.get_token())
    }

    api_response = send_post(urljoin(config.API_URL, 'auth'), headers=headers)

    variables = {
        'active_page': 'account'
    }

    if api_response.status_code == 200:
        variables['status'] = True
        variables['message'] = 'User logged out'
    else:
        variables['status'] = False
        variables['message'] = 'Failed to log out user'

    # logout_user()

    return render_template('auth.html', **variables)
