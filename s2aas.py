#!/usr/bin/env python
# coding=utf-8

# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from bitcoin import *
import json
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS

# Bitcoin address of the sensor
myAddress = 'mxjr2jvmbNFjQHA8qQ7FkE7jCX7E1jqWrK'

# Private key of the sensor 
myPrivateKey = 'cR3UpPmZtS98M7GZo4Khk3AhQvFFnfLdw8g4ZZhS13obMQWksEDg'

# Data encoding
# data has to be give in 2 byte hex
# Prefix '!' tells that this is no bitcoin address
# but data to be added to a provable unspendable output
datum_hex = '01'
dataIdentifier = '!'
payload = dataIdentifier + datum_hex

def send_data(requestAddress):
    # Get unspent tx outputs via blockr.io API
    unspentTxO = blockr_unspent(myAddress)

    # Take the latest unspent transction output (will be changed in tohe future)
    # Credit will be send back to the requester
    # Fee are the transaction fees
    # Rest is change which send to the sensor's address
    unspentValue = unspentTxO[-1]['value']
    credit = 1000
    fee = 100
    change = unspentValue - credit - fee

    # Tx input
    txIn = [unspentTxO[-1]]

    # Tx output
    # First output sends crendit back to requester in order that requester is able to identify tx
    # Secound output entails the actual data

    # Third output is the change
    txOut = [{'value': credit, 'address': requestAddress}, {'value': 0, 'address': payload}, {'value': change, 'address': myAddress}]

    # Create raw tx
    tx = mktx(txIn, txOut)

    # Sign raw tx with private key
    signedTx = sign(tx,0,myPrivateKey)

    # Push tx to testnet via blockr.io API
    blockr_pushtx(signedTx)
    print "Transaction with payload "+payload+" sent to "+requestAddress


class EchoClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print "Sending notification request to Biteasy.com"
        notification_request = {"event": "transactions:create","filters": {"addresses": [myAddress],"confidence": "UNCONFIRMED"}}
        self.sendMessage(json.dumps(notification_request))

    def onMessage(self, msg, binary):
        print "Message from BitEasy: " + msg
        jsonMsg = json.loads(msg)
        if jsonMsg['event'] == 'transactions:create':
            sender = jsonMsg["data"]["inputs"][0]["from_address"];
            if sender == myAddress :
                return
            data = jsonMsg["data"]["outputs"];
            for entry in data:
                if entry["to_address"] == myAddress:
                    print "Received " + str(entry["value"]) + " satoshis from "+sender
            send_data(sender)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        reactor.stop()
        reactor.run()

if __name__ == '__main__':

    factory = WebSocketClientFactory('ws://ws.biteasy.com/testnet/v1')
    factory.protocol = EchoClientProtocol
    connectWS(factory)
    reactor.run()


