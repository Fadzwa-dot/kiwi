import pytest
from flask import g
from app.auth.auth import require_auth
from unittest.mock import patch

@pytest.mark.parametrize("header, expected_status", [
    (None, 403),
    ("Bearer invalidtoken", 403),
])
def test_protected_route_auth(client, header, expected_status):
    @require_auth
    def protected():
        return "ok"
    with patch('app.auth.auth.verify_jwt', side_effect=Exception("Invalid token")):
        response = client.get('/users/', headers={"Authorization": header} if header else {})
        assert response.status_code == expected_status

# Additional tests for valid token, expired token, etc. can be added with proper JWT mocking
