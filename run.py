from app import app, db
from app.models import *

with app.app_context():
    db.create_all()

    if not Company.query.first():
        company = Company(company_name="Namma Kadai", cash_balance = 1000)
        db.session.add(company)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)