from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--create", help="create_database", action="store_true")
args = parser.parse_args()

db = SQLAlchemy()
app = Flask(__name__)
app.app_context().push()
db_path = os.path.join(os.path.dirname(__file__), 'financial_data.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db.init_app(app)


class FinancialData(db.Model):
    __tablename__ = 'financial_data'
    symbol = db.Column(db.String, nullable=False, primary_key=True)
    date = db.Column(db.String, nullable=False, primary_key=True)
    open_price = db.Column(db.String, nullable=False)
    close_price = db.Column(db.String, nullable=False)
    volume = db.Column(db.String, nullable=False)


if args.create:
    with app.app_context():
        db.create_all()
    print('Finished creating database')
