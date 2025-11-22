def create_error_response(code: int, message=None):
    response = {
        'status': {
            'code': code
        }
    }

    if message:
        response['status']['message'] = message

    return response
