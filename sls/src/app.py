import os
import base64
from datetime import datetime
from string import Template
import boto3

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
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    client = boto3.client('dynamodb')

class Transaction:
    def __init__(self, fuckcoinId, giver, recipient, purpose, when):
        self.fuckcoinId = fuckcoinId
        self.giver = giver
        self.recipient = recipient
        self.purpose = purpose
        self.when = when

    @classmethod
    def from_ddb(cls, ddb_resp):
        fuckcoinId = ddb_resp['fuckcoinId']['S']
        giver = ddb_resp['giver']['S']
        recipient = ddb_resp['recipient']['S']
        purpose = ddb_resp['purpose']['S']
        when = ddb_resp['when']['S']

        transaction = cls(fuckcoinId, giver, recipient, purpose, when)
        return transaction

import sys
def frint(string):
    print(string, file=sys.stderr)

@app.route('/all')
def show_all():
    resp = client.scan(TableName=TRANSACTIONS_TABLE)
    return jsonify(resp)

@app.route('/coin')
def landing():
    coinNumber = request.args.get('sn')
    signature = request.args.get('sig', None)

    resp = client.query(
        TableName=TRANSACTIONS_TABLE,
        KeyConditionExpression="fuckcoinId = :fuckcoinId",
        ExpressionAttributeValues={
            ":fuckcoinId": {'S': coinNumber}
        }
    )

    frint(resp)
    items = resp.get("Items");
    items = [Transaction.from_ddb(item) for item in items]

    if signature:
        frint(coinNumber)
        frint(signature)
        isLegit = verify_sig(coinNumber, signature)

    return render_template('show_all.html', transactions=items)

@app.route('/transact', methods=["POST"])
def transact():
    resp = client.put_item(
            TableName=TRANSACTIONS_TABLE,
            Item={
                'fuckcoinId': {'S': request.form["fuckcoin_id"] },
                'giver': {'S': request.form["giver"] },
                'recipient': {'S': request.form["recipient"] },
                'purpose': {'S': request.form["purpose"] },
                'when': {'S': datetime.utcnow().isoformat() }
            }
        )

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
