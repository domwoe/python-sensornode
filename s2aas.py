#!/usr/bin/python

# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from bitcoin import *

# Bitcoin address of the sensor
myAddress = 'mxjr2jvmbNFjQHA8qQ7FkE7jCX7E1jqWrK'

# Private key of the sensor 
myPrivateKey = 'cR3UpPmZtS98M7GZo4Khk3AhQvFFnfLdw8g4ZZhS13obMQWksEDg'

# Bitcoin address of the data requester.
# Will be read from incoming tx in the future.
requestAddress = 'myENFRWLyevSaYS5oB88bYWftmjtnxCEUL'


# Data encoding
# data has to be give in 2 byte hex
# Prefix '!' tells that this is no bitcoin address
# but data to be added to a provable unspendable output
datum_hex = '01'
dataIdentifier = '!'
payload = dataIdentifier + datum_hex
 
# Get unspent tx outputs via blockr.io API
unspentTxO = blockr_unspent(myAddress)

# Take the latest unspent transction output (will be changed in the future)
# Credit will be send back to the requester
# Fee are the transaction fees
# Rest is change which send to the sensor's address
unspentValue = unspentTxO[-1]['value']
credit = 1000
fee = 1000
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
