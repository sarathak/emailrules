""" Download email messages"""
from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from client import get_service
from db import get_engine, create_tables
from models import Email

BATCH = 10


def get_email(service, message_id: str) -> Email:
    """Get email metadata and create Email model"""
    message_details = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
    # Extract message subject ans sender
    message_subject = None
    message_sender = None
    for header in message_details['payload']['headers']:
        if header['name'] == 'Subject':
            message_subject = header['value']
        elif header['name'] == 'From':
            message_sender = header['value']
    # Extract message received date
    received_timestamp = int(message_details['internalDate']) / 1000
    received_at = datetime.fromtimestamp(received_timestamp)
    email = Email(subject=message_subject, sender=message_sender, message_id=message_id,
                  received_at=received_at)
    return email


def get_all_emails(service) -> Iterable[dict]:
    """Get all emails form gmail api"""
    next_page_token = None
    while True:
        result = service.users().messages().list(userId='me', pageToken=next_page_token).execute()
        for message in result['messages']:
            yield message
        next_page_token = result.get('nextPageToken')
        if not next_page_token:
            break


def write_to_db(emails, engine):
    print("Writing emails to database")
    with Session(engine) as session:
        session.add_all(emails)
        session.commit()


def fetch_emails():
    engine = get_engine()
    create_tables(engine)

    with Session(engine) as session:
        email_exists = session.query(Email).first() is not None
        if email_exists:
            confirmation = input("Emails already exists. Do you want to clear the table? (yes/no): ").lower().strip()
            if confirmation == 'yes':
                session.query(Email).delete()
                print("Table cleared.")
            else:
                print("Operation canceled.")
                return
        session.commit()

    service = get_service()

    print("Fetching messages from gmail api")
    messages = get_all_emails(service)
    emails: list[Email] = []
    for message in messages:
        message_id = message['id']
        email = get_email(service, message_id)
        emails.append(email)
        if len(emails) == BATCH:  # using batching to make write efficient
            write_to_db(emails, engine)
            emails = []
    if emails:
        write_to_db(emails, engine)
    print("Completed")


if __name__ == '__main__':
    fetch_emails()
