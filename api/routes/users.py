from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus

from helpers import create_response
from models import db, User
from log import get_logger


logger = get_logger()


def route_add_user():
    user = User(
        email=request.json['email'],
        password_hash=request.json['password_hash']
    )

    db.session.add(user)
    db.session.commit()

    return create_response()


@jwt_required
def route_get_user(user_id: str):
    logger.debug('get_jwt_identity(): %s', get_jwt_identity())
    logger.debug('user_id: %s', user_id)

    if get_jwt_identity() != user_id:
        return create_response(code=HTTPStatus.FORBIDDEN)

    user = db.session.query(User).filter(User.id == user_id).one()

    data = {
        'id': user.id,
        'email': user.email
    }

    return create_response(data=data)
