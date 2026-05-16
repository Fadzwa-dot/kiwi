import pytest
from app import create_app
from app.db import db
from app.models import Security, User
from app.config import TestConfig


@pytest.fixture(autouse=True, scope='function')
def clean_database(app):
    # Drop and recreate all tables before each test for isolation
    db.drop_all()
    db.create_all()
    yield

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        db.session.begin()
        _populate_database(db.session)
        yield db.session
        db.session.rollback()

def _populate_database(session):
    # Clear tables to avoid UNIQUE constraint errors
    session.query(Security).delete()
    session.query(User).delete()
    session.commit()

    admin_user = User(username='admin', password='admin', firstname='Admin', lastname='User', balance=1000.00)
    session.add(admin_user)
    securities = [
        Security(ticker='AAPL', issuer='Apple Inc.', price=150.00),
        Security(ticker='GOOGL', issuer='Alphabet Inc.', price=2800.00),
        Security(ticker='MSFT', issuer='Microsoft Corp.', price=300.00),
    ]
    session.add_all(securities)
    session.commit()
