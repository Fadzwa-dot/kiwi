import pytest
import jwt
from datetime import datetime, timedelta, timezone
from app.auth.auth import require_auth
from unittest.mock import patch

@pytest.fixture(scope="module", autouse=True)
def register_protected_route(app):
    # Register a temporary protected route for testing
    @app.route("/protected")
    @require_auth
    def protected():
        return "ok"
    yield

@pytest.mark.parametrize("header, expected_status", [
    (None, 403),
    ("Bearer invalidtoken", 403),
])
def test_protected_route_auth(client, header, expected_status):
    with patch('app.auth.auth.verify_jwt', side_effect=Exception("Invalid token")):
        response = client.get('/protected', headers={"Authorization": header} if header else {})
        assert response.status_code == expected_status


def test_protected_route_auth_valid_token(client, monkeypatch):
    secret = 'unit-test-secret'
    token = jwt.encode(
        {
            'sub': 'auth-user',
            'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        secret,
        algorithm='HS256',
    )

    def verify_with_shared_secret(encoded_token):
        return jwt.decode(encoded_token, secret, algorithms=['HS256'])

    monkeypatch.setattr('app.auth.auth.verify_jwt', verify_with_shared_secret)
    response = client.get('/protected', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200


def test_protected_route_auth_expired_token(client, monkeypatch):
    secret = 'unit-test-secret'
    token = jwt.encode(
        {
            'sub': 'auth-user',
            'exp': datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        secret,
        algorithm='HS256',
    )

    def verify_with_shared_secret(encoded_token):
        return jwt.decode(encoded_token, secret, algorithms=['HS256'])

    monkeypatch.setattr('app.auth.auth.verify_jwt', verify_with_shared_secret)
    response = client.get('/protected', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403


def test_protected_route_auth_invalid_signature_token(client, monkeypatch):
    signing_secret = 'good-secret'
    verification_secret = 'different-secret'
    token = jwt.encode(
        {
            'sub': 'auth-user',
            'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        signing_secret,
        algorithm='HS256',
    )

    def verify_with_wrong_secret(encoded_token):
        return jwt.decode(encoded_token, verification_secret, algorithms=['HS256'])

    monkeypatch.setattr('app.auth.auth.verify_jwt', verify_with_wrong_secret)
    response = client.get('/protected', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
