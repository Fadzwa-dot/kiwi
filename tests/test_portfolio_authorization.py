import pytest
from app.service.portfolio_authorization_service import PortfolioAuthorizationService, ROLE_VIEWER, ROLE_MANAGER
from app.db import db
from app.models import Portfolio, User

def test_grant_and_revoke_access(db_session):
    user = User.query.filter_by(username='admin').first()
    portfolio = Portfolio(name='Test', description='desc', user=user)
    db.session.add(portfolio)
    db.session.commit()
    access = PortfolioAuthorizationService.grant_access(portfolio.id, user.id, ROLE_MANAGER)
    db.session.commit()
    assert access.role == ROLE_MANAGER
    PortfolioAuthorizationService.revoke_access(portfolio.id, user.id)
    db.session.commit()
    assert PortfolioAuthorizationService.get_access(portfolio.id, user.id) is None

def test_has_access_roles(db_session):
    user = User.query.filter_by(username='admin').first()
    portfolio = Portfolio(name='Test', description='desc', user=user)
    db.session.add(portfolio)
    db.session.commit()
    PortfolioAuthorizationService.grant_access(portfolio.id, user.id, ROLE_VIEWER)
    db.session.commit()
    assert PortfolioAuthorizationService.has_access(portfolio.id, user.id, ROLE_VIEWER)
    assert not PortfolioAuthorizationService.has_access(portfolio.id, user.id, ROLE_MANAGER)


def test_is_owner(db_session):
    user = User.query.filter_by(username='admin').first()
    portfolio = Portfolio(name='Test', description='desc', user=user)
    db.session.add(portfolio)
    db.session.commit()
    assert PortfolioAuthorizationService.is_owner(portfolio.id, user.id)
