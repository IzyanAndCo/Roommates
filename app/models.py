import bcrypt
from sqlalchemy import UniqueConstraint

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    guests = db.relationship('Guest', backref='inviter', lazy=True)

    def set_password(self, password: str) -> None:
        """
        Hashes the password using bcrypt before storing in database.
        :param password: Password to set
        :type password: str
        """
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password: str) -> bool:
        """
        Checks whether the provided password matches the stored hashed password.
        :param password: Password to check
        :type password: str
        :return: Result of password check
        :rtype: bool
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def to_dict(self) -> dict:
        """
        Convert table data to dictionary
        :return: Dict with table data
        :rtype: dict
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


class GuestType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    __table_args__ = (UniqueConstraint('name', name='uq_name'),)

    def to_dict(self) -> dict:
        """
            Convert table data to dictionary
            :return: Dict with table data
            :rtype: dict
        """
        return {
            'id': self.id,
            'name': self.name
        }


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_type_id = db.Column(db.Integer, db.ForeignKey('guest_type.id'), nullable=False)
    guest_type = db.relationship('GuestType', backref='guests')
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coming_date = db.Column(db.Date, nullable=False)
    coming_time = db.Column(db.Time, nullable=False)
    stay_time = db.Column(db.Time, nullable=False)
    comment = db.Column(db.String(255))

    def to_dict(self):
        """
            Convert table data to dictionary
            :return: Dict with table data
            :rtype: dict
        """
        return {
            'id': self.id,
            'guest_type_id': self.guest_type_id,
            'inviter_id': self.inviter_id,
            'coming_date': self.coming_date.strftime('%Y-%m-%d'),
            'coming_time': self.coming_time.strftime('%H:%M:%S'),
            'stay_time': self.stay_time.strftime('%H:%M:%S'),
            'comment': self.comment
        }
