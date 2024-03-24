from datetime import datetime, timedelta
from unittest import TestCase, main
from unittest.mock import patch

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db import create_tables
from execute_rules import execute_rules
from models import Email
from rules import Property, Action


class TestRule(TestCase):

    def test_validation_properties_predicate_for_subject(self):
        Property(**{
            "field": "subject",
            "predicate": "contains",
            "value": "test email"
        })
        with self.assertRaises(ValidationError):
            Property(**{
                "field": "subject",
                "predicate": "less_than",
                "value": "test email"
            })

    def test_validation_properties_predicate_for_received(self):
        Property(**{
            "field": "date_received",
            "predicate": "less_than",
            "value": "10days"
        })
        with self.assertRaises(ValidationError):
            Property(**{
                "field": "date_received",
                "predicate": "contains",
                "value": "1day"
            })

    def test_validation_properties_value_for_received(self):
        Property(**{
            "field": "date_received",
            "predicate": "less_than",
            "value": "1days"
        })
        with self.assertRaises(ValidationError):
            Property(**{
                "field": "date_received",
                "predicate": "less_than",
                "value": "1aaa"
            })

    def test_validation_action(self):
        Action(**{
            "operation": "read",
        })
        Action(**{
            "operation": "unread",
        })
        Action(**{
            "operation": "move",
            "destination": "inbox",
        })


class TestRuleExecution(TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        create_tables(self.engine)
        with Session(self.engine) as session:
            email1 = Email(sender='test@test.com', subject='test_subject', message_id='1234',
                           received_at=datetime.now() - timedelta(days=2))
            email2 = Email(sender='test@test.com', subject='test_subject2', message_id='1235',
                           received_at=datetime.now() - timedelta(days=4))
            email3 = Email(sender='test2@test.com', subject='test_subject3', message_id='1236',
                           received_at=datetime.now() - timedelta(days=6))
            session.add_all((email1, email2, email3))
            session.commit()

    @patch('execute_rules.mark_as_unread')
    @patch('execute_rules.get_engine')
    @patch('execute_rules.get_service')
    def test_rule_sender(self, mock_get_service, mock_get_engine, mock_mark_as_unread):
        mock_get_engine.return_value = self.engine
        json_data = [
            {
                "description": "Rule 1",
                "conditions": "all",
                "properties": [
                    {
                        "field": "from",
                        "predicate": "contains",
                        "value": "test@test.com"
                    }
                ],
                "actions": [
                    {
                        "operation": "unread"
                    }
                ]
            }
        ]
        execute_rules(json_data)
        self.assertEquals(mock_mark_as_unread.call_count, 2)

    @patch('execute_rules.mark_as_unread')
    @patch('execute_rules.get_engine')
    @patch('execute_rules.get_service')
    def test_rule_received_less_than(self, mock_get_service, mock_get_engine, mock_mark_as_unread):
        mock_get_engine.return_value = self.engine
        json_data = [
            {
                "description": "Rule 1",
                "conditions": "all",
                "properties": [
                    {
                        "field": "date_received",
                        "predicate": "less_than",
                        "value": "3days"
                    }
                ],
                "actions": [
                    {
                        "operation": "unread"
                    }
                ]
            }
        ]
        execute_rules(json_data)
        self.assertEquals(mock_mark_as_unread.call_count, 2)

    @patch('execute_rules.mark_as_unread')
    @patch('execute_rules.get_engine')
    @patch('execute_rules.get_service')
    def test_rule_received_grater_than(self, mock_get_service, mock_get_engine, mock_mark_as_unread):
        mock_get_engine.return_value = self.engine
        json_data = [
            {
                "description": "Rule 1",
                "conditions": "all",
                "properties": [
                    {
                        "field": "date_received",
                        "predicate": "grater_than",
                        "value": "3days"
                    }
                ],
                "actions": [
                    {
                        "operation": "unread"
                    }
                ]
            }
        ]
        execute_rules(json_data)
        self.assertEquals(mock_mark_as_unread.call_count, 1)


if __name__ == '__main__':
    main()
