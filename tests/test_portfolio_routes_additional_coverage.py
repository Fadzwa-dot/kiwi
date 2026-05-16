import app.routes.portfolio_routes as portfolio_routes


class DummyRecord:
    def __init__(self, payload):
        self.payload = payload

    def __to_dict__(self):
        return self.payload


def test_portfolio_get_routes(client, monkeypatch):
    monkeypatch.setattr(
        portfolio_routes.portfolio_service,
        'get_all_portfolios',
        lambda: [DummyRecord({'id': 1, 'name': 'Main'})],
    )
    monkeypatch.setattr(
        portfolio_routes.portfolio_service,
        'get_portfolio_by_id',
        lambda portfolio_id: DummyRecord({'id': portfolio_id, 'name': 'Main'}),
    )
    monkeypatch.setattr(
        portfolio_routes.user_service,
        'get_user_by_username',
        lambda username: DummyRecord({'username': username}),
    )
    monkeypatch.setattr(
        portfolio_routes.portfolio_service,
        'get_portfolios_by_user',
        lambda user: [DummyRecord({'id': 2, 'owner': user.payload['username']})],
    )
    monkeypatch.setattr(
        portfolio_routes.transaction_service,
        'get_transactions_by_portfolio_id',
        lambda portfolio_id: [DummyRecord({'portfolio_id': portfolio_id, 'ticker': 'AAPL'})],
    )

    assert client.get('/portfolios/').status_code == 200
    assert client.get('/portfolios/1').status_code == 200
    assert client.get('/portfolios/user/admin').status_code == 200
    assert client.get('/portfolios/1/transactions').status_code == 200


def test_portfolio_not_found_routes(client, monkeypatch):
    monkeypatch.setattr(portfolio_routes.portfolio_service, 'get_portfolio_by_id', lambda portfolio_id: None)
    monkeypatch.setattr(portfolio_routes.user_service, 'get_user_by_username', lambda username: None)

    assert client.get('/portfolios/999').status_code == 404
    assert client.get('/portfolios/user/missing').status_code == 404


def test_portfolio_create_delete_and_access_routes(client, monkeypatch):
    monkeypatch.setattr(
        portfolio_routes.user_service,
        'get_user_by_username',
        lambda username: DummyRecord({'username': username}),
    )
    monkeypatch.setattr(
        portfolio_routes.portfolio_service,
        'create_portfolio',
        lambda name, description, user: 77,
    )
    monkeypatch.setattr(portfolio_routes.PortfolioAuthorizationService, 'is_owner', lambda portfolio_id, user_id: True)
    monkeypatch.setattr(portfolio_routes.portfolio_service, 'delete_portfolio', lambda portfolio_id: None)
    monkeypatch.setattr(
        portfolio_routes.PortfolioAuthorizationService,
        'grant_access',
        lambda portfolio_id, user_id, role: None,
    )
    monkeypatch.setattr(
        portfolio_routes.PortfolioAuthorizationService,
        'revoke_access',
        lambda portfolio_id, user_id: None,
    )
    monkeypatch.setattr(portfolio_routes.db.session, 'commit', lambda: None)

    create_resp = client.post(
        '/portfolios/',
        headers={'Authorization': 'Bearer token'},
        json={'name': 'Growth', 'description': 'Long term', 'username': 'admin'},
    )
    assert create_resp.status_code == 201

    delete_resp = client.delete('/portfolios/77', headers={'Authorization': 'Bearer token'})
    assert delete_resp.status_code == 200

    invalid_role_resp = client.post(
        '/portfolios/77/access',
        headers={'Authorization': 'Bearer token'},
        json={'user_id': 1, 'role': 'owner'},
    )
    assert invalid_role_resp.status_code == 400

    grant_resp = client.post(
        '/portfolios/77/access',
        headers={'Authorization': 'Bearer token'},
        json={'user_id': 1, 'role': 'viewer'},
    )
    assert grant_resp.status_code == 200

    revoke_resp = client.delete('/portfolios/77/access/1', headers={'Authorization': 'Bearer token'})
    assert revoke_resp.status_code == 200


def test_portfolio_create_validation_and_forbidden_delete(client, monkeypatch):
    monkeypatch.setattr(portfolio_routes.PortfolioAuthorizationService, 'is_owner', lambda portfolio_id, user_id: False)

    invalid_create = client.post(
        '/portfolios/',
        headers={'Authorization': 'Bearer token'},
        json={'name': 'OnlyName'},
    )
    assert invalid_create.status_code == 422

    missing_user_create = client.post(
        '/portfolios/',
        headers={'Authorization': 'Bearer token'},
        json={'name': 'Growth', 'description': 'Long term', 'username': 'missing'},
    )
    assert missing_user_create.status_code == 404

    forbidden_delete = client.delete('/portfolios/77', headers={'Authorization': 'Bearer token'})
    assert forbidden_delete.status_code == 403