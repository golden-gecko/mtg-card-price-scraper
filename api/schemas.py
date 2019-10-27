from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError


user_schema = {
    'type': 'object',
    'properties': {
        'email': {
            'type': 'string',
            'format': 'email'
        },
        'password_hash': {
            'type': 'string',
            'minLength': 64,
            'maxLength': 64
        }
    },
    'required': ['email', 'password_hash'],
    'additionalProperties': False
}


def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return False, str(e), None
    except SchemaError as e:
        return False, str(e), None

    return True, '', data
