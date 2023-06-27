# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from multiprocessing import Process, Pipe
import networkx
from pyvis.network import Network
import Risk_scoring
import Risk_scoring_upstream
import traceback

class TransactionRiskScore:
    api = BitcoinAPI()
    threadPool = None
    depth = 0
    graph = None
    
    def __init__(self,depth):
        self.depth = depth
        self.graph = networkx.DiGraph()
        
    def score(self,tx):
        # For the Transaction, get its participants
        txDetails = self.api.getTransaction(tx)
        participants = self._getParticipants(txDetails)
        print(f"Number of participants {len(participants)}")
        score = 0
        pipes = []
        processes = []
        #Calculate the Risk score for all participants
        for index, participant in enumerate(participants):
            self.graph.add_node(participant)
            self.graph.nodes[participant]['title'] = participant
            self.graph.nodes[participant]['label'] = self._cutAddr(participant)
            self.graph.nodes[participant]['color'] = "#2e2bfc"
            print(f"Calculating Risk Score for account '{participant}'")
            parent_conn, child_conn = Pipe()
            process = Process(target=self._accountRiskScore,args=(child_conn,participant))
            process.start()
            processes.append(process)
            pipes.append(parent_conn)
            #processes += process
            
        while(len(pipes) > 0):
            _pipes = []
            for pipe in pipes:
                if pipe.poll():
                    r = pipe.recv()
                    score += r["score"]
                    if r["graph"] is not None:
                        self.graph = networkx.compose(self.graph,r["graph"])
                else:
                    _pipes.append(pipe)
            pipes = _pipes

        
        for process in processes:
            process.terminate()
        

        #return average
        return score/len(participants)
    
   # def _accountRiskScore(self,addr):
   #     txs = self.api.getTransactions(addr, 25)
   #     scoreUp = self._riskScoreUpstream(txs)
   #     scoreDown = self._riskScoreDownstream(txs)
   #     
   #     scoreUp = scoreUp if scoreUp is not None else 0
   #     scoreDown = scoreDown if scoreDown is not None else 0
   #             
   #     return scoreUp if scoreUp > scoreDown else scoreDown
        
    def _accountRiskScore(self,pipe,*addr,**self2):
        addr = ''.join(addr)
        try:
            txs = BitcoinAPI().getTransactions(addr, 100)
            print(f"address {addr} has {len(txs)} transactions")
            scoreUp = self._riskScoreUpstream(txs,addr)
            scoreDown = self._riskScoreDownstream(txs,addr)
            pipe.send(dict(
                score=(scoreUp if scoreUp > scoreDown else scoreDown),
                graph=(self.graph)
            ))
            print(f"Calculated Score for {addr}")
            
        except Exception as e:
            print(f"Failed to calculate Score for {addr}:")
            print(traceback.format_exc())
            print("")
            pipe.send(dict(
                score=0,
                graph=None
            ))

        
        
    def _riskScoreDownstream(self,txs,startNode) -> int:
        score = 0
        for tx in txs:
            tx_id = tx["txid"]
            print(f"Computing transaction {tx_id} Downstream score")
            _score = Risk_scoring.recursive_search(tx["txid"], 1, self.depth,0,self.graph,[startNode])
            if _score > score:
                score = _score
        return score
                
                
    def _riskScoreUpstream(self,txs,startNode) -> int:
        score = 0
        for tx in txs:
            tx_id = tx["txid"]
            print(f"Computing transaction {tx_id} Upstream score")
            _score = score = Risk_scoring_upstream.recursive_upstream_search(tx["txid"], 1, self.depth,0,self.graph,[startNode])
            if _score > score:
                score = _score
        return score
        
    def _getParticipants(self,txDetails):
        participants = []
        participants =  list(map(lambda x:  self._tryGetScriptPubkeyAddress(x),txDetails["vout"])) if "vout" in txDetails else []
        participants = participants + (list(map(lambda x: self._tryGetScriptPubkeyAddress(x["prevout"]),txDetails["vin"])) if "vin" in txDetails else [])
        return [i for i in list(set(participants)) if i is not None]
    
    def _tryGetScriptPubkeyAddress(self,x):
        try:
            return x["scriptpubkey_address"]
        except TypeError:
            return None
        except KeyError:
            return None
    
    def _cutAddr(self,addr):
        return addr[0:4]+"..."+addr[-4:]
    
    def _saveGraph(self,fileName):
        net = Network(directed=True,
                  select_menu=True,
                  notebook=True,
                  neighborhood_highlight=True)
        fileName=fileName+".html"
        print("Creating graph...")
        net.from_nx(self.graph, default_edge_weight=1, show_edge_weights=True)
        net.show_buttons(filter_=['physics'])
        net.show(fileName)
        print("Done!")
        
    
def main(args):
    print("____________TRANSACTION RISK SCORE____________")
    trs = TransactionRiskScore(args.depth)
    print("FINAL SCORE:"+str(trs.score(args.transaction)),flush=True)
    trs._saveGraph(args.transaction)
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-tx', '--transaction',
                        help='Transaction hash', type=str, required = True)
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance (Default 2)', type=int, required = False, default = 2)
    args = parser.parse_args()
    main(args)