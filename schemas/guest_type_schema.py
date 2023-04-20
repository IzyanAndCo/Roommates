import re

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class GuestTypeSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=5, max=50))

    @validates_schema
    def validate_name(self, data, **kwargs):
        pattern = r'^[A-Za-zА-Яа-я0-9\.\,\-\s]+$'
        if not (re.match(pattern, data['name'])):
            raise ValidationError("Username should contain only letters, numbers and punctuation marks")
    