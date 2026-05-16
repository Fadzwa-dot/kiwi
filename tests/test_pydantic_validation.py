import pytest
from app.schemas import PortfolioCreateSchema, UserCreateSchema, TradeBuySchema, TradeSellSchema
from pydantic import ValidationError

def test_portfolio_create_schema_valid():
    data = {"username": "user1", "name": "Growth", "description": "Aggressive portfolio"}
    model = PortfolioCreateSchema(**data)
    assert model.username == "user1"

def test_portfolio_create_schema_invalid():
    with pytest.raises(ValidationError):
        PortfolioCreateSchema(username="user1", name=123, description=None)

def test_user_create_schema_valid():
    data = {"username": "user1", "password": "pass", "firstname": "John", "lastname": "Doe", "balance": 100.0}
    model = UserCreateSchema(**data)
    assert model.balance == 100.0

def test_trade_buy_schema_invalid():
    with pytest.raises(ValidationError):
        TradeBuySchema(portfolio_id="abc", ticker=123, quantity="ten")

def test_trade_sell_schema_valid():
    data = {"portfolio_id": 1, "ticker": "AAPL", "quantity": 5, "sale_price": 150.0}
    model = TradeSellSchema(**data)
    assert model.ticker == "AAPL"
