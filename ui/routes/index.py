from flask import render_template

from app import app
from log import get_logger


logger = get_logger()


@app.route('/')
def route_index():
    return render_template('index.html', active_page='home')
