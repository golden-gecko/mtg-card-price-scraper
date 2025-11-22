import http

from flask import request

from helpers import create_response
from models import db, User
from log import get_logger
from schemas import validate_user


logger = get_logger()


def route_users():
    status, message, data = validate_user(request.get_json())

    if not status:
        return create_response(http.HTTPStatus.BAD_REQUEST, message=message)

    user = User(
        email=data['email'],
        password_hash=data['password_hash']
    )

    db.session.add(user)
    db.session.commit()

    return create_response()
