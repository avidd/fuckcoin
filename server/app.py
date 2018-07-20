import os
import base64
from datetime import datetime
from string import Template

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import ECC
    from Crypto.Signature import DSS
except Exception as e:
    print("need to pip install pycryptodome")
    raise

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

ecc_public_key = base64.b64decode("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEqMI3pmvasBrNU9k1PyG+g56fnWSVrz8Y0zj9rY5XOlbN8hiQebEJ6ZD17nqjMoKcuzB80NCu7PoSzSBgkzq4Ig==")
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
    purpose=db.Column(db.UnicodeText(), nullable=False)
    when=db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/all')
def show_all():
    return render_template('show_all.html',
        transactions=Transaction.query.order_by(Transaction.when.desc()).all()
    )

@app.route('/coin')
def landing():
    print("IM A BANANA")
    coinNumber = request.args.get('sn')
    signature = request.args.get('sig', None)
    if coinNumber and signature:
        decodedSig = base64.urlsafe_b64decode(signature)
        isLegit = verify_sig(coinNumber, decodedSig)

    return render_template('landing.html', isLegit=isLegit, coin=coinNumber)

@app.route('/transact', methods=["POST"])
def transact():
    tran = Transaction(fuckcoin_id=request.form["fuckcoin_id"],
            giver=request.form["giver"],
            recipient=request.form["recipient"],
            purpose=request.form["purpose"])
    db.session.add(tran)
    db.session.commit()
    return redirect(url_for("show_all"))

def verify_sig(sn, b64sig):
    global ecc_public_key
    sig = base64.urlsafe_b64decode(b64sig)
    h = SHA256.new(sn)
    verifier = DSS.new(ecc_public_key, 'fips-186-3')
    try:
        verifier.verify(h, sig)
        print("The message is authentic.")
        return True
    except ValueError as e:
        print("The message is not authentic: {}".format(e))
        return False
