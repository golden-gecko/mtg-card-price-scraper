from app import db


card_format = db.Table('card_format',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('format_id', db.Integer, db.ForeignKey('format.id'))
)

card_set = db.Table('card_set',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('set_id', db.Integer, db.ForeignKey('set.id'))
)

card_type = db.Table('card_type',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('type_id', db.Integer, db.ForeignKey('type.id'))
)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    mana = db.Column(db.String(200))
    converted_mana_cost = db.Column(db.String(200))
    type = db.Column(db.String(200))
    text = db.Column(db.String(200))
    flavor = db.Column(db.String(200))
    watermark = db.Column(db.String(200))
    power = db.Column(db.String(200))
    toughness = db.Column(db.String(200))
    loyalty = db.Column(db.String(200))
    set = db.Column(db.String(200))
    rarity = db.Column(db.String(200))
    number = db.Column(db.String(200))
    artist = db.Column(db.String(200))

    def __repr__(self):
        return '<Card {}>'.format(self.name)
