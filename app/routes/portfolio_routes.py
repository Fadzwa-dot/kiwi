from app.service.portfolio_authorization_service import PortfolioAuthorizationService, ROLE_VIEWER, ROLE_MANAGER
from app.auth.auth import require_auth
from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

import app.service.portfolio_service as portfolio_service
import app.service.transaction_service as transaction_service
import app.service.user_service as user_service
from app.db import db

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/', methods=['GET'])
def get_all_portfolios():
    portfolios = portfolio_service.get_all_portfolios()
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    return jsonify(portfolio.__to_dict__()), 200


@portfolio_bp.route('/user/<username>', methods=['GET'])
def get_portfolios_by_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({'error': f'User {username} not found'}), 404
    portfolios = portfolio_service.get_portfolios_by_user(user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    from app.schemas import PortfolioCreateSchema
    try:
        req_data = PortfolioCreateSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "detail": e.errors()}), 422
    user = user_service.get_user_by_username(req_data.username)
    if user is None:
        return jsonify({'error': f'User {req_data.username} not found'}), 404
    portfolio_id = portfolio_service.create_portfolio(
        name=req_data.name,
        description=req_data.description,
        user=user,
    )
    db.session.commit()
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': portfolio_id}), 201


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    user_id = g.user.get('sub')
    if not PortfolioAuthorizationService.is_owner(portfolio_id, user_id):
        return jsonify({'error': 'Forbidden', 'detail': 'Only portfolio owner can delete'}), 403
    portfolio_service.delete_portfolio(portfolio_id)
    db.session.commit()
    return jsonify({'message': 'Portfolio deleted successfully'}), 200
@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_access(portfolio_id):
    req = request.get_json()
    user_id = req.get('user_id')
    role = req.get('role')
    if role not in [ROLE_VIEWER, ROLE_MANAGER]:
        return jsonify({'error': 'Invalid role'}), 400
    PortfolioAuthorizationService.grant_access(portfolio_id, user_id, role)
    db.session.commit()
    return jsonify({'message': f'Access granted: {role}'}), 200

@portfolio_bp.route('/<int:portfolio_id>/access/<int:user_id>', methods=['DELETE'])
@require_auth
def revoke_access(portfolio_id, user_id):
    PortfolioAuthorizationService.revoke_access(portfolio_id, user_id)
    db.session.commit()
    return jsonify({'message': 'Access revoked'}), 200


@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
def get_portfolio_transactions(portfolio_id):
    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200
