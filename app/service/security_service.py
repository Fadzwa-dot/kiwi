from app.models import Portfolio, User, Investment, Transaction, Security
from datetime import datetime, UTC

def execute_purchase_order(portfolio_id: int, ticker: str, quantity: int):
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise SecurityException(f"Portfolio with id {portfolio_id} does not exist.")
    user = portfolio.user
    security = db.session.query(Security).filter_by(ticker=ticker).one_or_none()
    if not security:
        raise SecurityException(f"Security with ticker {ticker} does not exist.")
    total_cost = security.price * quantity
    if user.balance < total_cost:
        raise InsufficientFundsError("Insufficient funds to complete the purchase.")
    # Deduct funds
    user.balance -= total_cost
    # Add or update investment
    investment = next((inv for inv in portfolio.investments if inv.ticker == ticker), None)
    if investment:
        investment.quantity += quantity
    else:
        investment = Investment(ticker=ticker, quantity=quantity, portfolio=portfolio)
        db.session.add(investment)
    # Add transaction
    transaction = Transaction(
        username=user.username,
        portfolio_id=portfolio.id,
        ticker=ticker,
        transaction_type="BUY",
        quantity=quantity,
        price=security.price,
        date_time=datetime.now(UTC),
    )
    db.session.add(transaction)
    db.session.flush()
    return True
class InsufficientFundsError(Exception):
    pass
from typing import List

from app.db import db
from app.models import Security


class SecurityException(Exception):
    pass


def get_all_securities() -> List[Security]:
    try:
        securities = db.session.query(Security).all()
        return securities
    except Exception as e:
        db.session.rollback()
        raise SecurityException(f'Failed to retrieve securities due to error: {str(e)}')


def get_security_by_ticker(ticker: str) -> Security | None:
    try:
        security = db.session.query(Security).filter_by(ticker=ticker).one_or_none()
        return security
    except Exception as e:
        db.session.rollback()
        raise SecurityException(f'Failed to retrieve security due to error: {str(e)}')
