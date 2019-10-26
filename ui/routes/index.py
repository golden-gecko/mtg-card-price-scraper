from flask import render_template

from app import app


@app.route('/')
def route_index():
    return render_template('index.html', active_page='home')
