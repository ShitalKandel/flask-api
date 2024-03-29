from app import db
from logging import UserMixin

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id       = db.Column(db.Integer, primary_key=True)
    user     = db.Column(db.String(64), unique = True)
    email    = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user       = user
        self.password   = password
        self.email      = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):
        db.session.add ( self )
        db.session.commit( )

        return self 