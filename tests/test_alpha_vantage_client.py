import pytest
from unittest.mock import patch
from app.services.alpha_vantage_client import AlphaVantageClient, SecurityQuote
from tests.conftest import app

@patch('app.services.alpha_vantage_client.requests.get')
def test_get_company_name_success(mock_get, app):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Name": "Apple Inc."}
    with app.app_context():
        with patch('flask.current_app.cache.get', return_value=None), patch('flask.current_app.cache.set'):
            name = AlphaVantageClient.get_company_name("AAPL")
            assert name == "Apple Inc."

@patch('app.services.alpha_vantage_client.requests.get')
def test_get_price_data_success(mock_get, app):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "Time Series (Daily)": {
            "2024-01-01": {
                "1. open": "100.0",
                "2. high": "110.0",
                "3. low": "90.0",
                "4. close": "105.0",
                "5. volume": "1000000"
            }
        }
    }
    with app.app_context():
        with patch('flask.current_app.cache.get', return_value=None), patch('flask.current_app.cache.set'):
            data = AlphaVantageClient.get_price_data("AAPL")
            assert data["close"] == 105.0

@patch('app.services.alpha_vantage_client.requests.get')
def test_get_company_name_cache(mock_get, app):
    with app.app_context():
        with patch('flask.current_app.cache.get', return_value="Apple Inc."):
            name = AlphaVantageClient.get_company_name("AAPL")
            assert name == "Apple Inc."
        mock_get.assert_not_called()

@patch('app.services.alpha_vantage_client.requests.get')
def test_get_price_data_cache(mock_get, app):
    cached = {"date": "2024-01-01", "close": 105.0}
    with app.app_context():
        with patch('flask.current_app.cache.get', return_value=cached):
            data = AlphaVantageClient.get_price_data("AAPL")
            assert data["close"] == 105.0
        mock_get.assert_not_called()
