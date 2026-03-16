import pytest
from app.service.trade_service import execute_purchase_order, liquidate_investment, TradeExecutionException, InsufficientFundsError
from app.db import db
from app.models import Portfolio, Security, User

def test_execute_purchase_order_valid(db_session):
    user = User.query.filter_by(username='admin').first()
    portfolio = Portfolio(name='Test', description='desc', user=user)
    db.session.add(portfolio)
    db.session.commit()
    security = Security.query.filter_by(ticker='AAPL').first()
    security.price = 10.0
    db.session.commit()
    user.balance = 100.0
    db.session.commit()
    execute_purchase_order(portfolio.id, 'AAPL', 5)
    assert user.balance == 50.0


def test_execute_purchase_order_insufficient_funds(db_session):
    user = User.query.filter_by(username='admin').first()
    portfolio = Portfolio(name='Test', description='desc', user=user)
    db.session.add(portfolio)
    db.session.commit()
    security = Security.query.filter_by(ticker='AAPL').first()
    security.price = 100.0
    db.session.commit()
    user.balance = 50.0
    db.session.commit()
    with pytest.raises(InsufficientFundsError):
        execute_purchase_order(portfolio.id, 'AAPL', 1)


def test_liquidate_investment_valid(db_session):
    user = User.query.filter_by(username='admin').first()
    portfolio = Portfolio(name='Test', description='desc', user=user)
    db.session.add(portfolio)
    db.session.commit()
    security = Security.query.filter_by(ticker='AAPL').first()
    security.price = 10.0
    db.session.commit()
    user.balance = 100.0
    db.session.commit()
    execute_purchase_order(portfolio.id, 'AAPL', 5)
    liquidate_investment(portfolio.id, 'AAPL', 5, 20.0)
    assert user.balance == 150.0
