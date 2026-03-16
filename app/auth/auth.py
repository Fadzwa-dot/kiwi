import os
import json
import requests
import jwt
from flask import request, g, jsonify, current_app
from functools import wraps
from jwt import PyJWKClient



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
        except Exception as e:
            return jsonify({"error": "Forbidden", "detail": str(e)}), 403
        return f(*args, **kwargs)
    return decorated
