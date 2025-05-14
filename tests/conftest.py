import pytest
import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.app import create_app
from server.models import db


@pytest.fixture(scope="module")
def app():
    app = create_app(config_class="server.config.TestingConfig")
    with app.app_context():
        yield app


@pytest.fixture(scope="module")
def _db(app):
    db.create_all()
    yield db
    db.drop_all()


@pytest.fixture(scope="function")
def session(_db):
    original_session = _db.session

    connection = _db.engine.connect()
    transaction = connection.begin_nested()

    session_factory = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    scoped_session = _db.scoped_session(session_factory)
    _db.session = scoped_session

    @event.listens_for(scoped_session, "after_transaction_end")
    def reset_session(session, transaction):
        if transaction.nested:
            session.expire_all()
            session.begin_nested()

    yield scoped_session

    scoped_session.remove()
    transaction.rollback()
    connection.close()

    _db.session = original_session
