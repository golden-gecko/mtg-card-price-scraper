from helpers import create_response


def route_healthcheck():
    return create_response(code=200)
