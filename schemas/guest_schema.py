from datetime import datetime, timedelta
from typing import Optional, Union

from flask import typing
from marshmallow import Schema, fields, validate, validates_schema, ValidationError, types
from sqlalchemy import and_, or_, null

from app import db
from app.models import Guest


class GuestSchema(Schema):
    guest_type_id = fields.Int(required=True)
    inviter_id = fields.Int(required=True)
    coming_date = fields.Date(required=True)
    coming_time = fields.Time(required=True)
    stay_time = fields.Time(required=True)
    comment = fields.Str(required=False, validate=validate.Length(min=0, max=256))

    def __init__(
            self,
            *,
            only: Optional[types.StrSequenceOrSet] = None,
            exclude: types.StrSequenceOrSet = (),
            many: bool = False,
            context: Optional[dict] = None,
            load_only: types.StrSequenceOrSet = (),
            dump_only: types.StrSequenceOrSet = (),
            partial: Union[bool, types.StrSequenceOrSet] = False,
            unknown: Optional[str] = None,
    ):
        super().__init__()
        self.existing_guest_id = None

    def validate(self, data, many=None, partial=None, existing_guest_id=None) -> dict[str, list[str]]:
        self.existing_guest_id = existing_guest_id

        result = super().validate(data, many=many, partial=partial)
        return result

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
        if data['coming_date'] == datetime.today().date() and data['coming_time'] < datetime.now().time():
            raise ValidationError('Time cannot be in the past')

    @validates_schema()
    def validate_time_match(self, data, **kwargs):
        coming_time = datetime.combine(data['coming_date'], data['coming_time'])
        stay_duration = timedelta(hours=data['stay_time'].hour,
                                  minutes=data['stay_time'].minute,
                                  seconds=data['stay_time'].second)
        exit_time = coming_time + stay_duration

        # Check if the guest is already checked in at this time
        query = db.select(Guest).where(and_
                                       (Guest.coming_date == data['coming_date'],
                                        or_(
                                            and_(Guest.coming_time <= data['coming_time'],
                                                 Guest.exit_time >= data['coming_time']),
                                            and_(Guest.coming_time <= exit_time.time(),
                                                 Guest.exit_time >= exit_time.time())
                                            )))

        if self.existing_guest_id:
            query = query.where(Guest.id != self.existing_guest_id)

        # If there is another guest already checked in at this time, raise an error
        if db.session.scalar(query):
            raise ValidationError('Another guest is already checked in at this time')
