from typing import List

from app.db import db
from app.models import Security


class SecurityException(Exception):
    pass


def get_all_securities() -> List[Security]:
    return db.session.query(Security).all()


def get_security_by_ticker(ticker: str) -> Security | None:
    try:
        security = db.session.query(Security).filter_by(ticker=ticker).one_or_none()
        return security
    except Exception as e:
        db.session.rollback()
        raise SecurityException(f'Failed to retrieve security due to error: {str(e)}')
