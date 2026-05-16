from app.db import db
from app.models import Portfolio, User, Investment, Security

class UnsupportedPortfolioOperationError(Exception):
    pass

def liquidate_investment(portfolio_id: int, ticker: str, quantity: int, sale_price: float):
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise UnsupportedPortfolioOperationError(f"Portfolio with id {portfolio_id} does not exist")
    user = portfolio.user
    investment = next((inv for inv in portfolio.investments if inv.ticker == ticker), None)
    if not investment:
        raise UnsupportedPortfolioOperationError(f"Investment with ticker {ticker} does not exist in portfolio {portfolio_id}")
    if investment.quantity < quantity:
        raise UnsupportedPortfolioOperationError(
            f"Cannot liquidate {quantity} shares of {ticker}. Only {investment.quantity} shares available in portfolio"
        )
    total_proceeds = sale_price * quantity
    user.balance += total_proceeds
    if investment.quantity == quantity:
        db.session.delete(investment)
    else:
        investment.quantity -= quantity
    from app.models import Transaction
    import datetime
    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=ticker,
            quantity=quantity,
            price=sale_price,
            transaction_type='SELL',
            date_time=datetime.datetime.now(),
        )
    )
    db.session.flush()
