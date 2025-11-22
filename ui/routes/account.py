from flask import render_template

from app import app


@app.route('/account')
def route_account():
    return render_template('account.html', active_page='account')
