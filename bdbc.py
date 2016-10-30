import logging
import time
import json
from flask import Flask, jsonify, make_response, request

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from bigchaindb_driver.exceptions import NotFoundError

bdb = BigchainDB('http://172.17.0.4:9984/api/v1')

def insert_transaction(signing_key, verifying_key, amount, timelimit):
    operation = {
        'data': {
            'amount': amount,
            'timelimit': timelimit,
        },
    }
    print(operation)
    creation_tx = bdb.transactions.create(verifying_key=verifying_key,
                                          signing_key=signing_key,
                                          asset=operation)

    print(creation_tx)
    return creation_tx['id']



def check_transaction(txid):
    try:
        status = bdb.transactions.status(txid)
        print(status)
        return True
    except NotFoundError as e:
        valid = 'false'
        logger.error('Transaction "%s" was not found.',
            txid,
            extra={'status': e.status_code})
        return False


def retrieve_transaction(txid):
    if(check_transaction(txid)):
        tx = bdb.transactions.retrieve(txid)
        # {'status': 'backlog'}
        # {'transaction': {'timestamp': '1477789525', 'fulfillments': [{'input': None, 'fulfillment': 'cf:4:TR_-1mh7sDQR4kAbMf4SVFZsuQj5saQCGaSeYy7bcowsd-vxmHNxn-uh92urK8pjtAC1s93UYGbWuIlFPiSOT0G_QemYTY09yv5gQiXAhazVpgNFaU-a56Q8gE_1QiEG', 'fid': 0, 'owners_before': ['6C4h14eMQHJYesyf3zEmQ9RS31fsME8RPkcFCcXTb5A3']}], 'conditions': [{'condition': {'details': {'public_key': '6C4h14eMQHJYesyf3zEmQ9RS31fsME8RPkcFCcXTb5A3', 'bitmask': 32, 'signature': None, 'type': 'fulfillment', 'type_id': 4}, 'uri': 'cc:4:20:TR_-1mh7sDQR4kAbMf4SVFZsuQj5saQCGaSeYy7bcow:96'}, 'owners_after': ['6C4h14eMQHJYesyf3zEmQ9RS31fsME8RPkcFCcXTb5A3'], 'cid': 0, 'amount': 1}], 'metadata': None, 'asset': {'data': {'timelimit': '1477789624962864895', 'amount': 1000}, 'updatable': False, 'divisible': False, 'id': '68e0a5b8-937a-4885-91c9-16b1a2871631', 'refillable': False}, 'operation': 'CREATE'}, 'version': 1, 'id': '2ecdd79bea882675b9db977abd97510c54e7500010ae7c3184ae0caf01377999'}

        print(tx)
        op = {
            'amount': tx['transaction']['asset']['data']['amount'],
            'timelimit': tx['transaction']['asset']['data']['timelimit'],
            'txid': txid,
            'created_at': tx['transaction']['timestamp']
        }
        return op
    else:
        return {}

# print(tx_retrieved)
# print("############# TRANSACTION")
# print(transacted_op)


app = Flask(__name__)

@app.route("/api/v1/insert", methods=['POST'])
def insert():
    if(request.json):
        verifying_key = request.json['verifying_key']
        signing_key = request.json['signing_key']
        amount = request.json['amount']
        timelimit = request.json['timelimit']
        txid = insert_transaction(signing_key, verifying_key, amount, timelimit)
        resp = {
            'signing_key': signing_key,
            'verifying_key': verifying_key,
            'txid': txid
        }
        print(txid)
        return make_response(jsonify(resp), 200)
    else:
        return make_response(jsonify({'error': 'Invalid Request'}), 500)

@app.route("/api/v1/retrieve", methods=['POST'])
def retrieve():
    if(request.json):
        transactions = []
        for tx in request.json['transactions']:
            t = retrieve_transaction(tx)
            transactions.append(t.copy())

        print("##########")
        print(transactions)

        return make_response(json.dumps(transactions), 200)
    else:
        return make_response(jsonify({'error': 'Invalid Request'}), 500)

@app.route("/api/v1/keys", methods=['GET'])
def get_keys():
    keys = generate_keypair()
    r = {
        'signing_key': keys.signing_key,
        'verifying_key': keys.verifying_key
    }
    return make_response(jsonify(r), 200)


app.run()
