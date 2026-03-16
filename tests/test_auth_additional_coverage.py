from types import SimpleNamespace

import app.auth.auth as auth_module


def test_verify_jwt_returns_test_claims_when_testing(app, monkeypatch):
    with app.app_context():
        monkeypatch.setitem(app.config, 'TESTING', True)
        claims = auth_module.verify_jwt('token')
        assert claims == {'sub': 'testuser'}


def test_verify_jwt_raises_when_cognito_config_missing(app, monkeypatch):
    with app.app_context():
        monkeypatch.setitem(app.config, 'TESTING', False)
        monkeypatch.setitem(app.config, 'COGNITO_REGION', None)
        monkeypatch.setitem(app.config, 'COGNITO_USER_POOL_ID', None)
        monkeypatch.setitem(app.config, 'COGNITO_APP_CLIENT_ID', None)
        monkeypatch.delenv('COGNITO_REGION', raising=False)
        monkeypatch.delenv('COGNITO_USER_POOL_ID', raising=False)
        monkeypatch.delenv('COGNITO_APP_CLIENT_ID', raising=False)
        try:
            auth_module.verify_jwt('token')
            assert False, 'expected missing config exception'
        except Exception as exc:
            assert 'Missing Cognito configuration' in str(exc)


def test_verify_jwt_decodes_with_jwks(app, monkeypatch):
    fake_signing_key = SimpleNamespace(key='public-key')

    class FakeJWKClient:
        def __init__(self, url):
            self.url = url

        def get_signing_key_from_jwt(self, token):
            assert token == 'valid-token'
            return fake_signing_key

    def fake_decode(token, key, algorithms, audience, issuer):
        assert token == 'valid-token'
        assert key == 'public-key'
        assert algorithms == ['RS256']
        assert audience == 'client-id'
        assert issuer.endswith('/pool-id')
        return {'sub': 'real-user'}

    monkeypatch.setattr(auth_module, 'PyJWKClient', FakeJWKClient)
    monkeypatch.setattr(auth_module.jwt, 'decode', fake_decode)

    with app.app_context():
        monkeypatch.setitem(app.config, 'TESTING', False)
        monkeypatch.setitem(app.config, 'COGNITO_REGION', 'us-east-1')
        monkeypatch.setitem(app.config, 'COGNITO_USER_POOL_ID', 'pool-id')
        monkeypatch.setitem(app.config, 'COGNITO_APP_CLIENT_ID', 'client-id')
        claims = auth_module.verify_jwt('valid-token')
        assert claims == {'sub': 'real-user'}


def test_require_auth_success_sets_claims(app, monkeypatch):
    monkeypatch.setattr(auth_module, 'verify_jwt', lambda token: {'sub': 'tester'})

    @auth_module.require_auth
    def protected():
        from flask import g, request

        assert g.user == {'sub': 'tester'}
        assert request.user == {'sub': 'tester'}
        return 'ok'

    with app.test_request_context(headers={'Authorization': 'Bearer good-token'}):
        assert protected() == 'ok'
