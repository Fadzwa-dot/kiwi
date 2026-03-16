import os
import json
import requests
import jwt
from flask import request, g, jsonify, current_app
from functools import wraps
from jwt import PyJWKClient


def verify_jwt(token):
    """Validate JWT using Cognito JWKS; use a safe bypass in test mode."""
    if current_app.config.get('TESTING'):
        return {"sub": "testuser"}

    region = current_app.config.get('COGNITO_REGION') or os.environ.get('COGNITO_REGION')
    user_pool_id = current_app.config.get('COGNITO_USER_POOL_ID') or os.environ.get('COGNITO_USER_POOL_ID')
    app_client_id = current_app.config.get('COGNITO_APP_CLIENT_ID') or os.environ.get('COGNITO_APP_CLIENT_ID')

    if not region or not user_pool_id or not app_client_id:
        raise Exception('Missing Cognito configuration')

    issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=app_client_id,
        issuer=issuer,
    )
    return claims



def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Forbidden", "detail": "Missing or invalid Authorization header"}), 403
        token = auth_header.split(' ')[1]
        try:
            user_claims = verify_jwt(token)
            g.user = user_claims
            request.user = user_claims
        except Exception as e:
            return jsonify({"error": "Forbidden", "detail": str(e)}), 403
        return f(*args, **kwargs)
    return decorated
