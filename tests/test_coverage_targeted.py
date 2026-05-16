import importlib

import pytest
from pydantic import BaseModel, ValidationError

from app import create_app
from app.config import DevelopmentConfig, TestConfig, get_config
from app.db import db
from app.models import Investment, Portfolio, Transaction, User
from app.service import transaction_service
from app.service.liquidate_investment_patch import (
    UnsupportedPortfolioOperationError,
    liquidate_investment,
)


def _create_portfolio_with_investment(quantity: int = 10, ticker: str = 'AAPL'):
    user = db.session.query(User).filter_by(username='admin').one()
    portfolio = Portfolio(name='Coverage PF', description='Coverage portfolio', user=user)
    db.session.add(portfolio)
    db.session.flush()
    investment = Investment(quantity=quantity, ticker=ticker, portfolio_id=portfolio.id)
    db.session.add(investment)
    db.session.commit()
    return user, portfolio, investment


def test_liquidate_patch_reduces_quantity_and_creates_transaction(db_session):
    user, portfolio, _ = _create_portfolio_with_investment(quantity=10)
    old_balance = user.balance

    liquidate_investment(portfolio.id, 'AAPL', 4, 50.0)

    updated = db.session.query(Investment).filter_by(portfolio_id=portfolio.id, ticker='AAPL').one()
    assert updated.quantity == 6
    user_after = db.session.query(User).filter_by(username='admin').one()
    assert user_after.balance == old_balance + 200.0
    tx = db.session.query(Transaction).filter_by(portfolio_id=portfolio.id, ticker='AAPL', transaction_type='SELL').all()
    assert len(tx) == 1


def test_liquidate_patch_deletes_investment_when_fully_sold(db_session):
    _, portfolio, _ = _create_portfolio_with_investment(quantity=3)

    liquidate_investment(portfolio.id, 'AAPL', 3, 25.0)

    inv = db.session.query(Investment).filter_by(portfolio_id=portfolio.id, ticker='AAPL').one_or_none()
    assert inv is None


def test_liquidate_patch_invalid_portfolio_raises(db_session):
    with pytest.raises(UnsupportedPortfolioOperationError):
        liquidate_investment(999999, 'AAPL', 1, 10.0)


def test_liquidate_patch_missing_investment_raises(db_session):
    user = db.session.query(User).filter_by(username='admin').one()
    portfolio = Portfolio(name='No Holdings', description='No investment', user=user)
    db.session.add(portfolio)
    db.session.commit()

    with pytest.raises(UnsupportedPortfolioOperationError):
        liquidate_investment(portfolio.id, 'AAPL', 1, 10.0)


def test_liquidate_patch_insufficient_quantity_raises(db_session):
    _, portfolio, _ = _create_portfolio_with_investment(quantity=2)

    with pytest.raises(UnsupportedPortfolioOperationError):
        liquidate_investment(portfolio.id, 'AAPL', 3, 10.0)


@pytest.mark.parametrize(
    'func,args',
    [
        (transaction_service.get_transactions_by_user, ('admin',)),
        (transaction_service.get_transactions_by_portfolio_id, (1,)),
        (transaction_service.get_transactions_by_ticker, ('AAPL',)),
    ],
)
def test_transaction_service_rollback_paths(monkeypatch, func, args):
    class ExplodingQuery:
        def filter(self, *_, **__):
            raise RuntimeError('boom')

    monkeypatch.setattr(db.session, 'query', lambda *_: ExplodingQuery())
    rollback_called = {'called': False}

    def fake_rollback():
        rollback_called['called'] = True

    monkeypatch.setattr(db.session, 'rollback', fake_rollback)

    with pytest.raises(RuntimeError):
        func(*args)
    assert rollback_called['called']


def test_get_config_paths(monkeypatch):
    monkeypatch.delenv('FLASK_ENV', raising=False)
    assert get_config(None) is DevelopmentConfig
    assert get_config('test') is TestConfig
    assert get_config('unknown-env') is DevelopmentConfig


def test_main_module_import_executes_app_bootstrap():
    import app.main as main_module

    reloaded = importlib.reload(main_module)
    assert reloaded.app is not None


def test_app_error_handlers_for_generic_and_validation():
    app = create_app(TestConfig)

    def raise_generic():
        raise RuntimeError('generic-failure')

    class _Payload(BaseModel):
        quantity: int

    def raise_validation():
        _Payload(quantity='bad-int')

    app.add_url_rule('/_coverage_generic_error', 'coverage_generic_error', raise_generic)
    app.add_url_rule('/_coverage_validation_error', 'coverage_validation_error', raise_validation)

    with app.test_client() as local_client:
        generic_resp = local_client.get('/_coverage_generic_error')
        assert generic_resp.status_code == 500

        validation_resp = local_client.get('/_coverage_validation_error')
        assert validation_resp.status_code == 422


def test_app_root_and_http_exception_handling():
    app = create_app(TestConfig)

    with app.test_client() as local_client:
        root_resp = local_client.get('/')
        assert root_resp.status_code == 200

        missing_resp = local_client.get('/definitely-missing')
        assert missing_resp.status_code == 404
        payload = missing_resp.get_json()
        assert payload['error'] == 'Not Found'
