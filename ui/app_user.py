import jwt

from flask_login import UserMixin

import config

from log import get_logger


class User(UserMixin):
    def __init__(self, id=None, token=None, data=None):
        self.logger = get_logger()
        self.logger.debug('User.__init__(): %s, %s, %s', id, token, data)

        self.id = id
        self.token = token
        self.data = data

        if not self.id and self.token:
            try:
                decoded = jwt.decode(self.token, config.AppConfig.JWT_SECRET_KEY)
            except jwt.ExpiredSignatureError as e:
                self.logger.warning('Failed to decode token "%s": %s', self.token, e)
                self.logger.debug('User.is_authenticated(): False (1)')
            except jwt.InvalidTokenError as e:
                self.logger.warning('Failed to decode token "%s": %s', self.token, e)
                self.logger.debug('User.is_authenticated(): False (2)')
            else:
                self.id = decoded['identity']

    @property
    def is_authenticated(self):
        self.logger.debug('User.is_authenticated()')

        return True

    @property
    def is_active(self):
        self.logger.debug('User.is_active(): %s, %s, %s', self.id, self.token, self.data)

        return self.is_authenticated

    @property
    def is_anonymous(self):
        self.logger.debug('User.is_anonymous(): %s, %s, %s', self.id, self.token, self.data)

        return self.is_authenticated is False or self.is_active is False

    def get_id(self):
        self.logger.debug('User.get_id(): %s, %s, %s', self.id, self.token, self.data)

        return self.id

    def get_token(self):
        self.logger.debug('User.get_token(): %s, %s, %s', self.id, self.token, self.data)

        return self.token

    def get_data(self):
        self.logger.debug('User.get_token(): %s, %s, %s', self.id, self.token, self.data)

        return self.data

    def __repr__(self):
        return '<User is_authenticated={}, is_active={}, is_anonymous={}, id={}, token={}, data={}>'.format(
            self.is_authenticated, self.is_active, self.is_anonymous, self.get_id(), self.get_token(), self.get_data()
        )
