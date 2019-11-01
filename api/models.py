import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID


db = SQLAlchemy()


class Deck(db.Model):
    __tablename__ = 'decks'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), index=True, nullable=False)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Deck name={}>'.format(self.name)


class Tokens(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = db.Column(db.String(8192), index=True, nullable=False)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Deck name={}>'.format(self.name)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    decks = db.relationship('Deck', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User email={}>'.format(self.email)
