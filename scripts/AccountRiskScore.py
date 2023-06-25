# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from networkx.readwrite import json_graph
from argparse import Namespace
import os
import json
import Neighborhood

class AccountRiskScore:
    api = BitcoinAPI()
    depth = 0
    workDir="AccountRiskScore_Cache"
    
    def __init__(self,depth):
        self.depth = depth
        
    
    def score(self,address):
        if not os.path.exists(self.workDir):
            os.makedirs(self.workDir)
        
        if(not os.path.exists(self.workDir+"/"+address+".json")):
            # Create Network by using Neighborhood script
            with open(self.workDir+'/_AccountRiskScoreAddressTemp.json', 'w') as f:
                f.write("[\""+address+"\"]")
                
            Neighborhood.main(Namespace(
                file=self.workDir+"/_AccountRiskScoreAddressTemp.json",
                depth=self.depth,
                htmlOutput=None,
                jsonOutput=self.workDir+"/"+address+".json",
                transactionFile=None,
                jupyterNotebook=False,
                physics=False,
                enableColoring=False,
                maxTransactions=25,
                ))
        else:
            print("Used local "+address+".json")

        # Import created Network
        network = self._read_json_file(self.workDir+"/"+address+".json")
        
        print(network)
        
        return 0;
    
    def _read_json_file(self,filename):
        with open(filename) as f:
            js_graph = json.load(f)
        return json_graph.node_link_graph(js_graph)

        
    
def main(args):
    scoreFunc = AccountRiskScore(args.depth)
    scoreFunc.score(args.address)
    
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-a', '--address',
                        help='Account Address', type=str, required = True)
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance (Default 2)', type=int, required = False, default = 2)
    args = parser.parse_args()
    main(args)