from sqlalchemy import create_engine, Engine
from models import Base


def get_engine() -> Engine:
    engine = create_engine('sqlite:///emails.db')
    return engine


def create_tables(engine: Engine):
    Base.metadata.create_all(engine)
