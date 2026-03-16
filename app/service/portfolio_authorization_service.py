from app.db import db
from app.models import PortfolioAccess, Portfolio, User

ROLE_VIEWER = 'viewer'
ROLE_MANAGER = 'manager'

class PortfolioAuthorizationService:
    @staticmethod
    def grant_access(portfolio_id, user_id, role):
        access = PortfolioAccess(portfolio_id=portfolio_id, user_id=user_id, role=role)
        db.session.add(access)
        return access

    @staticmethod
    def revoke_access(portfolio_id, user_id):
        access = PortfolioAccess.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
        if access:
            db.session.delete(access)
        return access

    @staticmethod
    def get_access(portfolio_id, user_id):
        return PortfolioAccess.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()

    @staticmethod
    def has_access(portfolio_id, user_id, required_role):
        access = PortfolioAccess.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
        if not access:
            return False
        if required_role == ROLE_VIEWER:
            return access.role in [ROLE_VIEWER, ROLE_MANAGER]
        elif required_role == ROLE_MANAGER:
            return access.role == ROLE_MANAGER
        return False

    @staticmethod
    def is_owner(portfolio_id, user_id_or_username):
        portfolio = Portfolio.query.filter_by(id=portfolio_id).first()
        if not portfolio:
            return False
        # Accept both user_id (int) and username (str)
        # Try to resolve user_id to username if needed
        if isinstance(user_id_or_username, int):
            user = User.query.filter_by(id=user_id_or_username).first()
            if not user:
                return False
            return portfolio.owner == user.username
        elif isinstance(user_id_or_username, str):
            return portfolio.owner == user_id_or_username
        return False
