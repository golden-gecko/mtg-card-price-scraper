from app import db


class Format(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)

    def __repr__(self):
        return '<Format {}>'.format(self.name)
