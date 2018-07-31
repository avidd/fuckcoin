import sys
import os
import base64
from datetime import datetime
from dateutil import tz, parser as dateParser
from string import Template

import boto3
from boto3.dynamodb.conditions import Key

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import ECC
    from Crypto.Signature import DSS
except Exception as e:
    print("need to pip install pycryptodome")
    raise


from flask import Flask, render_template, request, redirect, url_for, jsonify

ecc_public_key = base64.b64decode("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEqMI3pmvasBrNU9k1PyG+g56fnWSVrz8Y0zj9rY5XOlbN8hiQebEJ6ZD17nqjMoKcuzB80NCu7PoSzSBgkzq4Ig==")
app = Flask(__name__)

TRANSACTIONS_TABLE = os.environ['TRANSACTIONS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

print(IS_OFFLINE)
if IS_OFFLINE:
    db = boto3.resource(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    db = boto3.resource('dynamodb')

db = db.Table(TRANSACTIONS_TABLE)

def frint(string):
    print(string, file=sys.stderr)

@app.route('/all')
def show_all():
    resp = db.scan() 
    transactions = localTimedTransactions(resp.get("Items"))

    return render_template('all_transactions.html', transactions=transactions, excludeFields=['fuckcoinId'])

@app.route('/coin')
def coin():
    coinNumber = request.args.get('sn')
    signature = request.args.get('sig', None)
    submitted = request.args.get('submitted', False)

    transactions = []
    if coinNumber:
        resp = db.query(
            KeyConditionExpression=Key("fuckcoinId").eq(coinNumber),
            ScanIndexForward=False
        )

        transactions = localTimedTransactions(resp.get("Items"))
        if signature:
            frint(coinNumber)
            frint(signature)
            isLegit = verify_sig(coinNumber, signature)

    return render_template(
               'coin.html',
               transactions=transactions,
               submitted=submitted,
               fuckcoinId=coinNumber
           )

@app.route('/transact', methods=["POST"])
def transact():
    fuckcoinId = request.form["fuckcoinId"]

    resp = db.put_item(
            Item={
                'fuckcoinId': fuckcoinId,
                'giver': request.form["giver"],
                'recipient': request.form["recipient"],
                'purpose': request.form["purpose"],
                'when': datetime.utcnow().isoformat()
            }
        )

    return redirect(url_for("coin", sn=fuckcoinId, submitted='true'))

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

def localTimedTransactions(transactions):
    return [dict(t, whenLocal=utcToLocal(t["when"])) for t in transactions]

def utcToLocal(utcString):
    when = dateParser.parse(utcString)
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Los_Angeles')
    utc = when.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return local

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
