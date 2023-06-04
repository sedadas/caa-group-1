# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from enum import Enum
import networkx as nx
from networkx.readwrite import json_graph
from pyvis.network import Network
import json


class RELATIONSHIP(Enum):
    VOUT = 0
    VIN = 1

api = BitcoinAPI()
G = nx.DiGraph()

usedTransactions = list()

def main(args):
    net = Network(directed=True,neighborhood_highlight=True,height="2000px")
    with open(args.file, 'r') as ft:
        addrPool = json.load(ft)

    iteration = 1
    for address in addrPool: 
        G.add_node(address,color="#ff0000")
        G.nodes[address]['title'] = address
        G.nodes[address]['label'] = cutAddr(address)
    while(iteration <= args.depth):
        print("Iteration "+str(iteration)+"/"+str(args.depth))
        iteration += 1;
        addrPool = createNeighborhood(addrPool)


    if(args.jsonOutput != None):
        with open(args.jsonOutput, 'w') as outfile:
            outfile.write(json.dumps(json_graph.node_link_data(G)))
            print("Created "+args.jsonOutput)
        
    if(args.htmlOutput != None):
        net.from_nx(G)
        net.toggle_physics(False)
        net.show(args.htmlOutput,notebook=False)
        print("Created "+args.htmlOutput)
        
    if(args.transactionFile != None):
        with open(args.transactionFile, 'w') as outfile:
            outfile.write(json.dumps(usedTransactions))
    print("Done")
    
def draw(G,neighborhood,edgeTitle):
    _vouts = list(neighborhood[RELATIONSHIP.VOUT])
    _vins = list(neighborhood[RELATIONSHIP.VIN])
    for _to in _vouts:
        G.add_node(_to)
        G.nodes[_to]['title'] =_to
        G.nodes[_to]['label'] = cutAddr(_to)
        for _from in _vins:
            G.add_node(_from)
            G.nodes[_from]['title'] = _from
            G.nodes[_from]['label'] = cutAddr(_from)
            G.add_edge(_from,_to)
            G.edges[_from,_to]['title'] = edgeTitle

    
def cutAddr(addr):
    return addr[0:4]+"..."+addr[-4:]
    

def createNeighborhood(addrPool):
    #Get transactions for addr
    _newAddresses = set()
    print("Fetching"+str(len(addrPool))+" addresses")
    for addr in addrPool:
        txs = list(api.getTransactions(addr,25))
        for tx in txs: # for every transaction of addr
            #Get its inputs and outputs
            _vouts = list(map((lambda x:x["scriptpubkey_address"] if "scriptpubkey_address" in x else None),tx["vout"]))
            _vins = list(map(lambda x:x["prevout"]["scriptpubkey_address"],tx["vin"]))
            #create nodes and connect them
            for _to in _vouts:
                if _to != None:
                    _newAddresses.add(_to)
                    G.add_node(_to)
                    G.nodes[_to]['title'] =_to
                    G.nodes[_to]['label'] = cutAddr(_to)
                    for _from in _vins:
                        _newAddresses.add(_from)
                        G.add_node(_from)
                        G.nodes[_from]['title'] = _from
                        G.nodes[_from]['label'] = cutAddr(_from)
                        G.add_edge(_from,_to)
                        G.edges[_from,_to]['title'] = tx["txid"]
    return list(_newAddresses)
            
    
    



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--file',
                        help='Inputfile with wallet addresses', type=str, required = True)
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance', type=int, required = True)
    parser.add_argument('-html', '--htmlOutput',
                        help='HTML Output file name', type=str, required = False)
    parser.add_argument('-json', '--jsonOutput',
                        help='JSON Output file name', type=str, required = False)
    parser.add_argument('-t', '--transactionFile',
                        help='Output file that includes the used transactions for this network', type=str, required = False)
    args = parser.parse_args()
    main(args)
    