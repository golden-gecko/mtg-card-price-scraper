import hashlib
import http

from flask import render_template, request
from urllib.parse import urljoin

import config

from app import app
from helpers import send_post
from log import get_logger
from schemas import validate_user


logger = get_logger()


@app.route('/register', methods=['GET', 'POST'])
def route_register():
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

            response = send_post(urljoin(config.API_URL, 'users'), json=data)

            if response.status_code == http.HTTPStatus.OK:
                variables['status'] = True
                variables['message'] = 'User registered'
            else:
                variables['status'] = False
                variables['message'] = 'Failed to register user'

    return render_template('register.html', **variables)
