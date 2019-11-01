from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_refresh_token_required, jwt_required
from http import HTTPStatus
from sqlalchemy import and_

from helpers import create_response
from models import db, User
from schemas import validate_user


def route_login():
    status, message, data = validate_user(request.get_json())

    if not status:
        return create_response(HTTPStatus.BAD_REQUEST, message=message)

    user = db.session.query(User).filter(and_(
        User.email == data['email'],
        User.password_hash == data['password_hash']
    )).one()

    if not user:
        return create_response(HTTPStatus.UNAUTHORIZED)

    response = {
        'access_token': create_access_token(identity=user.id),
        'refresh_token': create_refresh_token(identity=user.id)
    }

    return create_response(data=response)


@jwt_required
def route_logout():
    return create_response()


@jwt_refresh_token_required
def route_refresh():
    response = {
        'access_token': create_access_token(identity=get_jwt_identity())
    }

    return create_response(data=response)
