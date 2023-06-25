# This script reads tx hashes, queries the related input addresses and computes the
# clusters based on the multiple-input clustering heuristic and saves them into a JSON file

from argparse import ArgumentParser
import json
import pandas as pd
import requests
import numpy as np

BASE_URL = f'https://blockstream.info/api/'

def get_in_addr(tx_hash):

    l_addr_in = [] # list of input addresses

    url = BASE_URL + 'tx/' + str(tx_hash) 
    
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()

        for i in range (len(json_data['vin'])):
            if 'scriptpubkey_address' in json_data['vin'][i]['prevout'].keys() :
                if json_data['vin'][i]['prevout']['scriptpubkey_address'] not in l_addr_in:
                    l_addr_in.append(json_data['vin'][i]['prevout']['scriptpubkey_address'])

    return l_addr_in

def main(args):

    tx_hashes_file = args.transactions  # contains tx hashes
    output_file = args.output  # will contain cluster id and cluster addresses
    adress_file = args.file
   
    with open(tx_hashes_file, 'r') as ft:
        tx_hashes = json.load(ft)
    
    with open(adress_file, 'r') as ft:
        illegal_addresses = json.load(ft)
   
    nb = args.nb_adresses if args.nb_adresses != None else len(illegal_addresses)
    illegal_addresses = illegal_addresses[:nb]
    print(illegal_addresses)
    
    cluster_addresses = []  # [[...],[...],...]
    # cluster_addresses is a list of clusters, where each cluster is a list of (unique) addresses
    # therefore, cluster_addresses is a list of lists of strings

    inputs = []

    for txs in tx_hashes : 
        inputs.append(get_in_addr(txs))
    
    clusters = inputs.copy()
    
    clusters_joined = []
    
    for i in range (len(clusters)):
        if i in clusters_joined:
            continue
        for j in range (len(clusters)):
            if j in clusters_joined or i==j:
                continue
            if set(clusters[i]).intersection(clusters[j]):
                for address in clusters[j] :
                    if address not in clusters[i] :
                        clusters[i].append(address)
                clusters_joined.append(j)

    mask = []
    for k in range (len(clusters)):
        if k not in clusters_joined : 
            mask.append(k)

    cluster_addresses = [clusters[i] for i in mask]
    print('Number of clusters: ', len(cluster_addresses)) 
    with open(output_file, 'w') as fp:
        json.dump(cluster_addresses, fp)
        
    index_clusters = np.linspace(0, len(cluster_addresses)-1,len(cluster_addresses)).astype(int)
    
    illegal_clusters = []
    nb_tot_adresses = 0
    for address in illegal_addresses :
        for ind in index_clusters :
            if address in cluster_addresses[ind]:
                illegal_clusters.append(ind)
                nb_tot_adresses += len(cluster_addresses[ind])
                pass
            
    print(f'Indexes of illegal clusters : {illegal_clusters}')
    print(f'Total illegal adresses {nb_tot_adresses} in {len(illegal_clusters)} clusters')    



if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-o', '--output',
                        help='Output file path (JSON)', type=str, required=True)
    parser.add_argument('-t', '--transactions',
                        help='Input file path (JSON)', type=str, required=True)
    parser.add_argument('-f', '--file',
                        help='Inputfile with wallet addresses', type=str, required = True)
    
    parser.add_argument('-nb', '--nb_adresses',
                        help='Number of illegal addresses we want to use', type=int, required = False)
    
    args = parser.parse_args()

    main(args)