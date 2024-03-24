import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, RootModel, model_validator

from models import Email


class Condition(str, Enum):
    all = 'all'
    any = 'any'


class Field(str, Enum):
    sender = "from"
    receiver = "to"
    subject = "subject"
    received = "date_received"


class Predicate(str, Enum):
    contains = "contains"
    not_equal = "not_equals"
    less_than = "less_than"
    grater_than = "grater_than"


class Property(BaseModel):
    field: Field
    predicate: Predicate
    value: str

    @model_validator(mode='after')
    def validate_field(self):
        if self.field == Field.received and self.predicate not in (Predicate.less_than, Predicate.grater_than):
            raise ValueError(f'predicate ({self.predicate}) not supported for field ({self.field})')
        elif self.field != Field.received and self.predicate in (Predicate.less_than, Predicate.grater_than):
            raise ValueError(f'predicate ({self.predicate}) not supported for field ({self.field})')
        elif self.field == Field.received:
            if not re.match("^\d+(days|months)$", self.value):
                raise ValueError(f'value not in valid pattern ({self.value}) use days or months for {self.field}. '
                                 f'eg: 1days, 1months')
        return self

    @property
    def get_model_field(self):
        if self.field == Field.received:
            return Email.received_at
        elif self.field == Field.sender:
            return Email.sender
        elif self.field == Field.subject:
            return Email.subject

    @property
    def get_datetime_value(self):
        if self.field == Field.received:
            if self.value.endswith('months'):
                # not following calendar month.
                delta = timedelta(days=int(self.value.replace('months', '')) * 30)
            else:
                delta = timedelta(days=int(self.value.replace('days', '')))
            return datetime.now() - delta


class Operation(str, Enum):
    mark_read = "read"
    mark_unread = "unread"
    move_message = "move"


class Destination(str, Enum):
    inbox = 'inbox'
    bin = 'bin'


class Action(BaseModel):
    operation: Operation
    destination: Destination = Destination.inbox


class Rule(BaseModel):
    description: Optional[str]
    conditions: Condition
    properties: list[Property]
    actions: list[Action]


class RuleList(RootModel):
    root: list[Rule]
