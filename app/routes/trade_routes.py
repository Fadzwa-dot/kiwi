from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.auth.auth import require_auth
from app.db import db
from app.service import trade_service
from app.service.portfolio_authorization_service import PortfolioAuthorizationService

trade_bp = Blueprint('trade', __name__)


@trade_bp.route('/buy', methods=['POST'])
@require_auth
def execute_purchase_order():
    from app.schemas import TradeBuySchema
    try:
        req_data = TradeBuySchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "detail": e.errors()}), 422
    if (
        not PortfolioAuthorizationService.is_owner(req_data.portfolio_id, g.user['sub'])
        and not PortfolioAuthorizationService.has_access(req_data.portfolio_id, g.user['sub'], 'manager')
    ):
        return jsonify({'error': 'Forbidden', 'detail': 'Insufficient portfolio access'}), 403
    trade_service.execute_purchase_order(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Purchase order executed successfully'}), 201


@trade_bp.route('/sell', methods=['POST'])
@require_auth
def liquidate_investment():
    from app.schemas import TradeSellSchema
    try:
        req_data = TradeSellSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "detail": e.errors()}), 422
    trade_service.liquidate_investment(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
        sale_price=req_data.sale_price,
    )
    db.session.commit()
    return jsonify({'message': 'Investment liquidated successfully'}), 200
