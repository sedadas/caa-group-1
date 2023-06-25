# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from enum import Enum
import networkx as nx
from networkx.readwrite import json_graph
from pyvis.network import Network
import modin.pandas as pd
import json
import yaml
import csv
import ray
ray.init()

class RELATIONSHIP(Enum):
    VOUT = 0
    VIN = 1

api = BitcoinAPI()
G = nx.DiGraph()

with open('../config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

df = pd.read_csv(config["paths"]["data"]+"/data.csv", dtype={
            'is_cluster_definer': 'str',
            'category': 'str',
            'actor': 'str'
    })

usedTransactions = list()
jupyterNotebook = False

def main(args):
    depth = args.depth
    jupyterNotebook = args.jupyterNotebook
    physics = args.physics
    net = Network(directed=True,
                  neighborhood_highlight=True,
                  notebook=jupyterNotebook,
                  select_menu=True)
    with open(args.file, 'r') as ft:
        addrPool = json.load(ft)

    iteration = 1
    for address in addrPool:
        G.add_node(address,color="#ff0000")
        G.nodes[address]['title'] = address
        G.nodes[address]['label'] = cutAddr(address)
    while(iteration <= depth):
        print("Iteration "+str(iteration)+"/"+str(depth))
        iteration += 1;
        addrPool = createNeighborhood(args,addrPool)
    
    print("Created a Network with "+str(len(G.nodes))+" Nodes and "+str(len(G.edges))+" Edges")


    if(args.jsonOutput != None):
        print("Creating "+args.jsonOutput+"...")
        with open(args.jsonOutput, 'w') as outfile:
            outfile.write(json.dumps(json_graph.node_link_data(G)))
            print("Done!")
    
        
    if(args.transactionFile != None):
        print("Creating "+args.transactionFile+"...")
        with open(args.transactionFile, 'w') as outfile:
            outfile.write(json.dumps(usedTransactions))
        print("Done!")
        
    if(args.htmlOutput != None):
        print("Creating "+args.htmlOutput+"...")
        net.from_nx(G, default_edge_weight=1, show_edge_weights=True)
        net.show_buttons(filter_=['physics'])
        net.toggle_physics(physics)
#        net.set_options("""const options = {      
#  "physics": {
#    "forceAtlas2Based": {
#      "springLength": 100
#    },
#    "minVelocity": 0.75,
#    "solver": "forceAtlas2Based"
#  }
#}""")
        net.show(args.htmlOutput)
        print("Done!")
    
   
def cutAddr(addr):
    return addr[0:4]+"..."+addr[-4:]
    
def getType(addr):
    if ('tags' in df) and (df['tags'].str.contains(addr).any()):
        return df[df['tags'].str.contains(addr)].to_dict()['title']
    else:
        return 'Unknown'

def setColorByType(node_type):
    nodeType = str(node_type)
    if 'Ponzi Scheme' in nodeType:
        return '#1ab124'
    if 'Mixing Services' in nodeType:
        return '#816231'
    if 'Ransomware' in nodeType or 'Ransomwhere' in nodeType:
        return '#7ff51c'
    if 'Sextortion' in nodeType:
        return '#9f2b68'
    if 'Market' in nodeType:
        return '#bb9311'
    else:
        return '#89cff0'

def getRisk(src, dst, src_type):
    srcType = str(src_type)
    coefficient = 1
    if 'Ponzi Scheme' in srcType:
        coefficient = 2
    if 'Mixing Services' in srcType:
        coefficient = 2
    if 'Ransomware' in srcType or 'Ransomwhere' in srcType:
        coefficient = 2
    if 'Sextortion' in srcType:
        coefficient = 2
    if 'Market' in srcType:
        coefficient = 2

    return coefficient


def _tryGetScriptPubkeyAddress(x):
    try:
        return x["scriptpubkey_address"]
    except TypeError:
        return None
    except KeyError:
        return None


def createNeighborhood(args,addrPool):
    #Get transactions for addr
    _newAddresses = set()
    print("Fetching " +str(len(addrPool))+" addresses")
    for addr in addrPool:
        txs = list(api.getTransactions(addr, args.maxTransactions))
        print("Found "+str(len(txs))+" transactions for address " +addr)
        for tx in txs: # for every transaction of addr
            #Get its inputs and outputs
            _vouts = list(map(lambda x:  _tryGetScriptPubkeyAddress(x),tx["vout"])) if "vout" in tx else []
            _vins = list(map(lambda x: _tryGetScriptPubkeyAddress(x["prevout"]),tx["vin"])) if "vin" in tx else []
            print("Found "+str(len(_vins))+" inputs and "+str(len(_vouts))+" outputs in transaction "+tx["txid"])
            #create nodes and connect them
            for _to in _vouts:
                if _to != None:
                    _newAddresses.add(_to)
                    G.add_node(_to)
                    G.nodes[_to]['title'] =_to
                    G.nodes[_to]['label'] = cutAddr(_to)
                    for _from in _vins:
                        if(_from != None):
                            _newAddresses.add(_from)
                            G.add_node(_from)
                            G.nodes[_from]['title'] = _from
                            G.nodes[_from]['label'] = cutAddr(_from)
                            nodeType = getType(_from)
                            if args.enableColoring:
                                color = setColorByType(nodeType)
                                G.nodes[_from]['description'] = nodeType
                                G.nodes[_from]['color'] = color
                            G.add_edge(_from,_to)
                            G.edges[_from,_to]['title'] = tx["txid"]
                            G.edges[_from,_to]['value'] = getRisk(_from, _to, nodeType)
    return list(_newAddresses)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--file',
                        help='Inputfile with wallet addresses', type=str, required = True)
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance (Default 1)', type=int, required = False, default = 1)
    parser.add_argument('-html', '--htmlOutput',
                        help='HTML Output file name', type=str, required = False)
    parser.add_argument('-json', '--jsonOutput',
                        help='JSON Output file name', type=str, required = False)
    parser.add_argument('-t', '--transactionFile',
                        help='Output file that includes the used transactions for this network', type=str, required = False)
    parser.add_argument('-max', '--maxTransactions',
                        help='Max transactions for each address. Should be a multiple of 25. (Default:25)', type=int, required = False, default = 25)
    parser.add_argument('-physics', '--physics',
                        help='Enable/Disable physics. Default is true', type=bool, required = False, default = True)
    parser.add_argument('-jupyter', '--jupyterNotebook',
                        help='Enable/Disable jupyter notebook mode. Default is false', type=bool, required = False, default = False)
    parser.add_argument('-color', '--enableColoring',
                        help='Enable/Disable coloring. Default is false', type=bool, required = False, default = False) 
    args = parser.parse_args()
    main(args)
    
