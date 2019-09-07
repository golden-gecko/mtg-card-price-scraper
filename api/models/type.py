from app import db


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)

    def __repr__(self):
        return '<Type {}>'.format(self.name)
