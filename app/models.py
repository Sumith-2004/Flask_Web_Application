from app import db
from datetime import datetime, timedelta

def indian_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    cash_balance = db.Column(db.Float, nullable=False, default=1000)
    def __repr__(self):
        return f'<Company {self.company_name}>'


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, default=0)      
    def __repr__(self):
        return f'<Item {self.item_name}>'


class Purchase(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=indian_time)
    qty = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    item = db.relationship('Item', backref=db.backref('purchases', lazy=True))

    def __repr__(self):
        return f'<Purchase {self.id} - Item {self.item_id}>'


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=indian_time)
    qty = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    item = db.relationship('Item', backref=db.backref('sales', lazy=True))

    def __repr__(self):
        return f'<Sales {self.id} - Item {self.item_id}>'
