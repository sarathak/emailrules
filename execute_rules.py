"""Execute rules on downloaded emails"""
import json

from pydantic import ValidationError
from sqlalchemy import Select, and_, or_
from sqlalchemy.orm import Session

from client import get_service
from db import get_engine, create_tables
from models import Email
from rules import RuleList, Condition, Predicate, Operation, Destination


def mark_as_read(service, message_id: str):
    message = service.users().messages().modify(userId='me', id=message_id,
                                                body={'removeLabelIds': ['UNREAD']}).execute()
    return message


def mark_as_unread(service, message_id: str):
    message = service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()
    return message


def move_message(service, message_id: str, destination: Destination):
    if destination == Destination.inbox:
        remove_label = 'TRASH'
        add_label = 'INBOX'
    else:
        remove_label = 'INBOX'
        add_label = 'TRASH'
    message = service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': [remove_label],
                                                                                  'addLabelIds': [add_label]}).execute()
    return message


def execute_rules(json_data: list):
    engine = get_engine()
    create_tables(engine)
    service = get_service()

    try:
        r = RuleList.parse_obj(json_data)
        print(r.json())
    except ValidationError as e:
        print("Validation error:")
        print(e.errors())

        return

    for rule in r.root:
        query = Select(Email)
        filter_args = []
        for p in rule.properties:
            if p.predicate == Predicate.less_than:
                filter_args.append(p.get_model_field < p.get_datetime_value)
            elif p.predicate == Predicate.grater_than:
                filter_args.append(p.get_model_field > p.get_datetime_value)
            elif p.predicate == Predicate.contains:
                filter_args.append(p.get_model_field.ilike(f'%{p.value}%'))

        if rule.conditions == Condition.any:
            query = query.where(or_(*filter_args))
        else:
            query = query.where(and_(*filter_args))
        with Session(engine) as session:
            for email in session.scalars(query):
                for action in rule.actions:
                    if action.operation == Operation.mark_unread:
                        mark_as_unread(service, email.message_id)
                    elif action.operation == Operation.mark_read:
                        mark_as_read(service, email.message_id)
                    elif action.operation == Operation.move_message:
                        move_message(service, email.message_id, action.destination)


if __name__ == '__main__':
    with open('rules.json', 'r') as fs:
        json_data = json.load(fs)
    execute_rules(json_data)
