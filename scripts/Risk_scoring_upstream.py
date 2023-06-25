# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from enum import Enum
import networkx as nx
from networkx.readwrite import json_graph
import json
import statistics
import yaml
import pandas as pd
import requests


with open('../config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

data = pd.read_csv(config["paths"]["data"]+"/data.csv")
BASE_URL = 'https://blockstream.info/api/'

def main(args):

    depth_max = args.depth_max if args.depth_max != None else 3;
    tx_hash = args.tx_hash 
    score = recursive_upstream_search(tx_hash, 1, depth_max,0)
    print(f"This transaction has a risk of {score}")

def recursive_upstream_search(tx_hash, depth, depth_max,score):
    BASE_URL = 'https://blockstream.info/api/'
    url = BASE_URL + 'tx/' + str(tx_hash) 
    
    response = requests.get(url)
    if response.status_code == 200:
        tx = response.json()
    
        inputs = tx["vin"]
        #print(f"depth {depth}, {len(inputs)} inputs")
        if len(inputs) <= 40:
            for j in range (len(inputs)) : 
                addr =  inputs[j]['prevout']["scriptpubkey_address"]
                if addr in data['address'].values :
                    #print(f"illegal adress found upstream {addr} at depth {depth}")
                    for vin in tx['vin']:
                        if vin['prevout']['scriptpubkey_address'] == addr:
                            satoshi_in = tx['vin'][j]['prevout']['value']
                    score_addr = satoshi_in/depth
                    #print(score_addr)
                    depth = depth_max
                else :
                    score_addr = 0
                score = max(score,score_addr)
    
                #print(f"{tx['txid']} --> {tx_i['txid']}")
                if  depth < depth_max:
                    #recursive_search(tx_i['txid'],depth, depth_max, score)
                    score = max(score,recursive_upstream_search(inputs[j]['txid'], depth+1, depth_max, score))
    
                #print(f"{addr} has not reused {tx['txid']}")
    else:
        print(f"Failed to get {url} (HTTP STATUS {response.status_code} )")
        return 0
        
    return score

def get_address_txs(address):
    txs = []
    # return list txs of all transactions for address
    # if a has more than 25 txs, we need to fetch all of them

    transaction_url = BASE_URL + 'address/' + str(address) + '/txs'
    response = requests.get(transaction_url)
    n = 0
    if response.status_code == 200:
        json_data = response.json()
        n = len(json_data)
        
    while response.status_code == 200 and n>0: 
        for i in range (len(json_data)):
            txs.append(json_data[i])
        url_next_transac =  transaction_url + '/chain/' + str(json_data[len(json_data)-1]['txid'])
        response = requests.get(url_next_transac)
        json_data = response.json()
        n = len(json_data)
    return txs


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-d', '--depth_max',
                        help='Maximal depth we want to explore upstream', type=int, required = False)
    
    parser.add_argument('-tx', '--tx_hash',
                        help='Transaction hash we want to compute the upstream score', type=str, required = True)


    
    args = parser.parse_args()
    main(args)
    
