from app.db import db

class PortfolioAccess(db.Model):
    __tablename__ = 'portfolio_access'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(16), nullable=False)  # 'viewer' or 'manager'

    def __to_dict__(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'user_id': self.user_id,
            'role': self.role
        }
