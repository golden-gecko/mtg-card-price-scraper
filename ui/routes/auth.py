from flask import redirect, render_template, request

from app import app
from schemas import validate_user


@app.route('/login', methods=['GET', 'POST'])
def route_login():
    variables = {
        'active_page': 'account'
    }

    if request.method == 'POST':
        status, message, data = validate_user(request.get_json())

        variables['status'] = status
        variables['message'] = message
        variables['data'] = data

    return render_template('auth.html', **variables)


@app.route('/logout')
def route_logout():
    return redirect('/')
