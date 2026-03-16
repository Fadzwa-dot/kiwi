from pydantic import BaseModel, ValidationError

class PortfolioCreateSchema(BaseModel):
    username: str
    name: str
    description: str

class UserCreateSchema(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    balance: float

class TradeBuySchema(BaseModel):
    portfolio_id: int
    ticker: str
    quantity: float

class TradeSellSchema(BaseModel):
    portfolio_id: int
    ticker: str
    quantity: float
    sale_price: float

# Shared error response schema
class ErrorResponseSchema(BaseModel):
    error: str
    detail: str
