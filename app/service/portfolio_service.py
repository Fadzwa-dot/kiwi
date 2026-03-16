from app.models import Investment, Security
def liquidate_investment(portfolio_id: int, ticker: str, quantity: int, price: float):
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise UnsupportedPortfolioOperationError(f"Portfolio with id {portfolio_id} does not exist")
    investment = next((inv for inv in portfolio.investments if inv.ticker == ticker), None)
    if not investment:
        raise UnsupportedPortfolioOperationError(f"Investment with ticker {ticker} does not exist in portfolio {portfolio_id}")
    if investment.quantity < quantity:
        raise UnsupportedPortfolioOperationError(
            f"Cannot liquidate {quantity} shares of {ticker}. Only {investment.quantity} shares available in portfolio"
        )
    investment.quantity -= quantity
    user = portfolio.user
    user.balance += quantity * price
    if investment.quantity == 0:
        db.session.delete(investment)
    db.session.flush()
    db.session.expire_all()
from typing import List

from app.db import db
from app.models import Portfolio, User


class UnsupportedPortfolioOperationError(Exception):
    pass


class PortfolioOperationError(Exception):
    pass


def create_portfolio(name: str, description: str, user: User) -> int:
    if not name or not description or not user:
        raise UnsupportedPortfolioOperationError(
            f'Invalid input[name:{name}, description: {description}, user: {user}]. Please try again.'
        )
    portfolio = Portfolio(name=name, description=description, user=user)
    try:
        db.session.add(portfolio)
        db.session.flush()
        return portfolio.id
    except Exception as e:
        db.session.rollback()
        raise PortfolioOperationError(f'Failed to create portfolio due to error: {str(e)}')


def get_portfolios_by_user(user: User) -> List[Portfolio]:
    try:
        portfolios = db.session.query(Portfolio).filter_by(owner=user.username).all()
        return portfolios
    except Exception as e:
        db.session.rollback()
        raise PortfolioOperationError(f'Failed to retrieve portfolios due to error: {str(e)}')


def get_all_portfolios() -> List[Portfolio]:
    try:
        portfolios = db.session.query(Portfolio).all()
        return portfolios
    except Exception as e:
        db.session.rollback()
        raise PortfolioOperationError(f'Failed to retrieve portfolios due to error: {str(e)}')


def get_portfolio_by_id(portfolio_id: int) -> Portfolio | None:
    try:
        portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
        return portfolio
    except Exception as e:
        db.session.rollback()
        raise PortfolioOperationError(f'Failed to retrieve portfolio due to error: {str(e)}')


def delete_portfolio(portfolio_id: int):
    try:
        portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
        if not portfolio:
            raise UnsupportedPortfolioOperationError(f'Portfolio with id {portfolio_id} does not exist')
        db.session.delete(portfolio)
        db.session.flush()
    except Exception as e:
        db.session.rollback()
        raise e
