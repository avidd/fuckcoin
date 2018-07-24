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

ecc_public_key = base64.b64decode("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEqMI3pmvasBrNU9k1PyG+g56fnWSVrz8Y0zj9rY5XOlbN8hiQebEJ6ZD17nqjMoKcuzB80NCu7PoSzSBgkzq4Ig==")
app = Flask(__name__)
dbUriTemplate = Template("mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST/$DB")

import sys
def frint(string):
    print(string, file=sys.stderr)

@app.route('/all')
def show_all():
    transactions = [
        {'fuckcoin_id': 20, 'giver': 'Mark', 'recipient': 'David', 'purpose': 'stuffs'}
    ]

    return render_template('show_all.html', transactions=transactions)

@app.route('/coin')
def landing():
    coinNumber = request.args.get('sn')
    signature = request.args.get('sig', None)
    if coinNumber and signature:
        frint(coinNumber, signature, decodedSig, isLegit)
        isLegit = verify_sig(coinNumber, signature)

    return render_template('landing.html', isLegit=isLegit, coin=coinNumber)

@app.route('/transact', methods=["POST"])
def transact():
    return redirect(url_for("show_all"))

def verify_sig(sn, b64sig):
    # https://stackoverflow.com/posts/9807138/revisions
    missing_padding = len(b64sig) % 4
    if missing_padding != 0:
        b64sig += '=' * (4 - missing_padding)

    sig = base64.urlsafe_b64decode(b64sig)
    h = SHA256.new(sn)
    verifier = DSS.new(ecc_public_key, 'fips-186-3')
    try:
        verifier.verify(h, sig)
        frint("The message is authentic.")
        return True
    except ValueError as e:
        frint("The message is not authentic: {}".format(e))
        return False

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
