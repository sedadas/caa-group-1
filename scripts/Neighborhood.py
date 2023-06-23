# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from enum import Enum
import networkx as nx
from networkx.readwrite import json_graph
from pyvis.network import Network
import json
import statistics

class RELATIONSHIP(Enum):
    VOUT = 0
    VIN = 1

api = BitcoinAPI()
G = nx.DiGraph()

jupyterNotebook = False

def main(args):
    Network_Transactions = []
    usedTransactions = list()
    
    depth = args.depth if args.depth != None else 1;
    nb = args.nb_adresses if args.nb_adresses != None else None;
    jupyterNotebook = args.jupyterNotebook if args.jupyterNotebook  != None else False
    physics = args.physics if args.physics  != None else True
    net = Network(directed=True,
                  neighborhood_highlight=True,
                  notebook=jupyterNotebook,
                  select_menu=True)
    with open(args.file, 'r') as ft:
        addrPool = json.load(ft)
    
    if nb !=None:
        addrPool = addrPool[:min(len(addrPool),nb)]
    iteration = 1
    for address in addrPool: 
        G.add_node(address,color="#ff0000")
        G.nodes[address]['title'] = address
        G.nodes[address]['label'] = cutAddr(address)
    while(iteration <= depth):
        print("Iteration "+str(iteration)+"/"+str(depth))
        iteration += 1;
        addrPool, Network_Transactions = createNeighborhood(addrPool)
        usedTransactions += Network_Transactions
    usedTransactions = list(set(usedTransactions))
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
        net.from_nx(G)
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
        net.show(args.htmlOutput,notebook=jupyterNotebook)
        print("Done!")
     
    if (args.stats != None):
        # Calculate the in-degree and out-degree distributions
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())

        # Calculate the median, minimum, and maximum of the in-degrees
        in_median = statistics.median(in_degrees.values())
        in_min = min(in_degrees.values())
        in_max = max(in_degrees.values())

        # Calculate the median, minimum, and maximum of the out-degrees
        out_median = statistics.median(out_degrees.values())
        out_min = min(out_degrees.values())
        out_max = max(out_degrees.values())

        # Calculate the number of weakly connected components
        num_components = nx.number_weakly_connected_components(G)

        # Store the results in a dictionary
        results = {
            'Number of Weakly Connected Components': num_components,
            'Number of transactions' : len(usedTransactions),
            'In-Degree Min': in_min,
            'In-Degree Median': in_median,
            'In-Degree Max': in_max,
            'Out-Degree Min': out_min,
            'Out-Degree Median': out_median,
            'Out-Degree Max': out_max
        }

        # Display the results
        for key, value in results.items():
            print(key + ":", value)
        

    
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
    network_transactions = []
    print("Fetching " +str(len(addrPool))+" addresses")
    for addr in addrPool:
        txs = list(api.getTransactions(addr, args.maxTransactions if args.maxTransactions != None else 25))
        print("Found "+str(len(txs))+" transactions for address " +addr)
        for tx in txs: # for every transaction of addr
            #Get its inputs and outputs
            network_transactions.append(tx['txid'])
            _vouts = list(map((lambda x:x["scriptpubkey_address"] if "scriptpubkey_address" in x else None),tx["vout"]))
            _vins = list(map(lambda x:x["prevout"]["scriptpubkey_address"],tx["vin"]))
            print("Found "+str(len(_vins))+" inputs and "+str(len(_vouts))+" outputs in transaction "+tx["txid"])
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
    return list(_newAddresses), network_transactions
            
    
    



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--file',
                        help='Inputfile with wallet addresses', type=str, required = True)
    
    parser.add_argument('-nb', '--nb_adresses',
                        help='Number of illegal addresses we want to use', type=int, required = False)
    
    parser.add_argument('-s', '--stats',
                        help='Statistiques about the network', type=bool, required = False)
    
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance (Default 1)', type=int, required = False)
    parser.add_argument('-html', '--htmlOutput',
                        help='HTML Output file name', type=str, required = False)
    parser.add_argument('-json', '--jsonOutput',
                        help='JSON Output file name', type=str, required = False)
    parser.add_argument('-t', '--transactionFile',
                        help='Output file that includes the used transactions for this network', type=str, required = False)
    parser.add_argument('-max', '--maxTransactions',
                        help='Max transactions for each address. Should be a multiple of 25. (Default:25)', type=int, required = False)
    parser.add_argument('-physics', '--physics',
                        help='Enable/Disable physics. Default is true', type=bool, required = False)
    parser.add_argument('-jupyter', '--jupyterNotebook',
                        help='Enable/Disable jupyter notebook mode. Default is false', type=bool, required = False)
    
    args = parser.parse_args()
    main(args)
    