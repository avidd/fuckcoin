import os
import traceback
import base64
from chalice import Chalice, Response

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import ECC
    from Crypto.Signature import DSS
except Exception as e:
    print("need to pip install pycryptodome")
    raise

app = Chalice(app_name='helloworld')
if 'DEBUG' in os.environ:
    app.debug = True

@app.route('/')
def index():
    params = app.current_request.query_params
    if params:
        serial = params.get('sn')
        signature = params.get('sig')
        if serial and signature:
            response = ""
            try:
                response = verify_sig(serial, signature)
            except:
                traceback.print_exc()
                response = traceback.format_exc()
            return Response(body=response,
                            status_code=200,
                            headers={'Content-Type': 'text/html'})

    return Response(body="Have a legacy coin?  That's okay too.",
                    status_code=200,
                    headers={'Content-Type': 'text/html'})

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
