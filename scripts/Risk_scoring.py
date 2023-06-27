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
    score = recursive_search(tx_hash, 1, depth_max,0)
    print(f"This transaction has a risk of {score}")

def recursive_search(tx_hash, depth, depth_max,score,graph,nodeQueue):
    BASE_URL = 'https://blockstream.info/api/'
    url = BASE_URL + 'tx/' + str(tx_hash) 
    
    response = requests.get(url)
    if response.status_code == 200:
        tx = response.json()
        output_adresses = list(map((lambda x:x["scriptpubkey_address"] if "scriptpubkey_address" in x else None),tx["vout"]))
        #print(f"depth {depth}, {len(output_adresses)} output adresses")
        if len(output_adresses) <= 10:
            for addr in output_adresses : 
                graph.add_node(addr)
                graph.nodes[addr]['title'] = addr
                graph.nodes[addr]['label'] = cutAddr(addr)
                graph.add_edge(nodeQueue[-1],addr)
                graph.edges[nodeQueue[-1],addr]['title'] = tx_hash
                if addr in data['address'].values :
                    graph.nodes[addr]['color'] = "#c21206"
                    for index in range (len(nodeQueue)):
                        if index+1 < len(nodeQueue):
                            graph.edges[nodeQueue[index],nodeQueue[index+1]]['color'] = "#c21206"
                        else:
                            graph.edges[nodeQueue[index],addr]['color'] = "#c21206"
                    for j in range (len(tx['vout'])):
                        satoshi = 0
                        if 'scriptpubkey_address' in tx['vout'][j].keys():
                            if tx['vout'][j]['scriptpubkey_address'] == addr:
                                satoshi = tx['vout'][j]['value']
                        score_addr = satoshi/depth
                    depth = depth_max
                else :
                    score_addr = 0
                score = max(score,score_addr)
                
    
                txs = BitcoinAPI().getTransactions(addr, 2500)
                if txs is None :
                    print("none")
                for i in range (len(txs)):
                    tx_i  = txs[i]
                    inputs = list(map(lambda x:x["txid"],tx_i["vin"]))
                    if tx['txid'] in inputs :
                        #print(f"{tx['txid']} --> {tx_i['txid']}")
                        if  depth < depth_max:
                            nodeQueue.append(addr)
                            score = max(score,recursive_search(tx_i['txid'], depth+1, depth_max, score,graph,nodeQueue))
    
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

def cutAddr(addr):
    return addr[0:4]+"..."+addr[-4:]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-d', '--depth_max',
                        help='Maximal depth we want to explore', type=int, required = False)
    
    parser.add_argument('-tx', '--tx_hash',
                        help='Transaction hash we want to compute the score', type=str, required = True)


    
    args = parser.parse_args()
    main(args)
    
