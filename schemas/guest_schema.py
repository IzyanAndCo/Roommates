from datetime import datetime
import re

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class GuestSchema(Schema):
    guest_type_id = fields.Int(required=True)
    inviter_id = fields.Int(required=True)
    coming_date = fields.Date(required=True)
    coming_time = fields.Time(required=True)
    stay_time = fields.Time(required=True)
    comment = fields.Str(required=False, validate=validate.Length(min=0, max=256))

    @validates_schema
    def validate_coming_date(self, data, **kwargs):
        """
        Validation for coming_date field

        :param data: Data with fields
        :param kwargs: Additional parameters
        """
        if data['coming_date'] < datetime.today().date():
            raise ValidationError('Date cannot be in the past')

    @validates_schema
    def validate_coming_time(self, data, **kwargs):
        """
            Validation for coming_date field

            :param data: Data with fields
            :param kwargs: Additional parameters
        """
        if data['coming_date'] == datetime.today().date() and data['coming_time'] == datetime.now().time():
            raise ValidationError('Time cannot be in the past')
