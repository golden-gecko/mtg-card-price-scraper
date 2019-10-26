from flask import request

from helpers import create_response
from models import db, User


def route_users():
    user = User(
        email=request.args.get('email'),
        password_hash=request.args.get('password_hash')
    )

    db.session.add(user)
    db.session.commit()

    return create_response()
