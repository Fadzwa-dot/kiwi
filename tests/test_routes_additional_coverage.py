import app.routes.security_routes as security_routes
import app.routes.trade_routes as trade_routes
import app.routes.user_routes as user_routes


class DummyRecord:
    def __init__(self, payload):
        self.payload = payload

    def __to_dict__(self):
        return self.payload


def test_user_routes_happy_paths(client, monkeypatch):
    monkeypatch.setattr(
        user_routes.user_service,
        'get_all_users',
        lambda: [DummyRecord({'username': 'u1'})],
    )
    monkeypatch.setattr(
        user_routes.user_service,
        'get_user_by_username',
        lambda username: DummyRecord({'username': username}),
    )
    monkeypatch.setattr(user_routes.user_service, 'create_user', lambda **kwargs: None)
    monkeypatch.setattr(user_routes.user_service, 'update_user_balance', lambda **kwargs: None)
    monkeypatch.setattr(user_routes.user_service, 'delete_user', lambda username: None)
    monkeypatch.setattr(
        user_routes.transaction_service,
        'get_transactions_by_user',
        lambda username: [DummyRecord({'ticker': 'AAPL', 'username': username})],
    )
    monkeypatch.setattr(user_routes.db.session, 'commit', lambda: None)

    assert client.get('/users/').status_code == 200
    assert client.get('/users/tester').status_code == 200

    create_resp = client.post(
        '/users/',
        json={
            'username': 'tester',
            'password': 'secret',
            'firstname': 'Test',
            'lastname': 'User',
            'balance': 1000.0,
        },
    )
    assert create_resp.status_code == 201

    update_resp = client.put('/users/update-balance', json={'username': 'tester', 'new_balance': 1200.0})
    assert update_resp.status_code == 200

    assert client.delete('/users/tester').status_code == 200
    assert client.get('/users/tester/transactions').status_code == 200


def test_user_get_not_found_branch(client, monkeypatch):
    monkeypatch.setattr(user_routes.user_service, 'get_user_by_username', lambda username: None)

    resp = client.get('/users/missing-user')
    assert resp.status_code == 404


def test_security_routes_happy_and_not_found(client, monkeypatch):
    monkeypatch.setattr(
        security_routes.security_service,
        'get_all_securities',
        lambda: [DummyRecord({'ticker': 'AAPL'})],
    )
    monkeypatch.setattr(
        security_routes.security_service,
        'get_security_by_ticker',
        lambda ticker: DummyRecord({'ticker': ticker}),
    )
    monkeypatch.setattr(
        security_routes.transaction_service,
        'get_transactions_by_ticker',
        lambda ticker: [DummyRecord({'ticker': ticker, 'type': 'BUY'})],
    )

    assert client.get('/securities/').status_code == 200
    assert client.get('/securities/AAPL').status_code == 200
    assert client.get('/securities/AAPL/transactions').status_code == 200

    monkeypatch.setattr(security_routes.security_service, 'get_security_by_ticker', lambda ticker: None)
    assert client.get('/securities/MISSING').status_code == 404


def test_trade_routes_buy_and_sell(client, monkeypatch):
    monkeypatch.setattr(trade_routes.trade_service, 'execute_purchase_order', lambda **kwargs: None)
    monkeypatch.setattr(trade_routes.trade_service, 'liquidate_investment', lambda **kwargs: None)
    monkeypatch.setattr(trade_routes.db.session, 'commit', lambda: None)

    buy_resp = client.post('/trades/buy', json={'portfolio_id': 1, 'ticker': 'AAPL', 'quantity': 2})
    assert buy_resp.status_code == 201

    sell_resp = client.post(
        '/trades/sell',
        json={'portfolio_id': 1, 'ticker': 'AAPL', 'quantity': 1, 'sale_price': 150.0},
    )
    assert sell_resp.status_code == 200
