import os
from datetime import datetime
from string import Template

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
dbUriTemplate = Template("mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST/$DB")
app.config['SQLALCHEMY_DATABASE_URI'] = dbUriTemplate.substitute(os.environ)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fuckcoin_id = db.Column(db.Integer, nullable=False)
    giver = db.Column(db.Unicode(255), nullable=False)
    recipient = db.Column(db.Unicode(255), nullable=False)
    when=db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def show_all():
    return render_template('show_all.html',
        transactions=Transaction.query.order_by(Transaction.when.desc()).all()
    )
