import re

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=256))

    @validates_schema
    def validate_password(self, data, **kwargs):
        if not re.search("[a-z]", data['password']):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search("[A-Z]", data['password']):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search("[0-9]", data['password']):
            raise ValidationError("Password must contain at least one number")
        if not re.search("[^a-zA-Z0-9]", data['password']):
            raise ValidationError("Password must contain at least one non-numeric and non-nun-alphabetical symbol")

    @validates_schema
    def validate_username(self, data, **kwargs):
        username = data.get('username')
        if not re.match("^[a-zA-Z0-9_]+$", username):
            raise ValidationError('Username should contain only alphanumeric symbols and underscores')
