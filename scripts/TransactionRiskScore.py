# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from multiprocessing import Process, Pipe
import Risk_scoring
import Risk_scoring_upstream
import traceback
import yaml
import pandas



class TransactionRiskScore:
    api = BitcoinAPI()
    threadPool = None
    depth = 0
    data = None
    config = None
    
    def __init__(self,depth):
        self.depth = depth
        with open('../config.yaml') as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)
            self.data = pandas.read_csv(self.config["paths"]["data"]+"/data.csv")
            
    def score(self,tx):
        # For the Transaction, get its participants
        txDetails = self.api.getTransaction(tx)
        participants = self._getParticipants(txDetails)
        
        score = 0
        pipes = []
        processes = []
        #Calculate the Risk score for all participants
        for index, participant in enumerate(participants):
            if self._isIllegalAddress(participant):
                print(f"transaction contains an illegal adress ({participant})")
                _satoshi = self._scoreForIllegalAddressParticipant(participant,txDetails)

                if(_satoshi == 0):
                    print(f"Failed to calculate Score for {participant}")
                else:
                    score += _satoshi/self.config["transactionRiskScore"]["illegalAddressDivisor"]
                    
                    

                # If the Participant is an illegal address, its score gets Satoshi * 1.5
            else:
                print(f"Calculating Risk Score for account '{participant}'")
                parent_conn, child_conn = Pipe()
                process = Process(target=self._accountRiskScore,args=(child_conn,participant))
                process.start()
                processes.append(process)
                pipes.append(parent_conn)
            
        while(len(pipes) > 0):
            _pipes = []
            for pipe in pipes:
                if pipe.poll():
                    score += pipe.recv()
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
   
    def _scoreForIllegalAddressParticipant(self,participant,txDetails):
        _satoshi = 0
        for vout in txDetails["vout"]:
            if "scriptpubkey_address" in vout and vout["scriptpubkey_address"] == participant:
                _satoshi += vout["value"]
        for vin in txDetails["vin"]:
            if "prevout" in vin and "scriptpubkey_address" in vin["prevout"] and vin["prevout"]["scriptpubkey_address"] == participant:
                _satoshi += vin["prevout"]["value"]
        return _satoshi
   
    def _isIllegalAddress(self,addr):
        return addr in self.data["address"].values
    
       
    def _accountRiskScore(self,pipe,*addr):
        addr = ''.join(addr)
        try:
            txs = BitcoinAPI().getTransactions(addr, 25)
            scoreUp = self._riskScoreUpstream(txs)
            scoreDown = self._riskScoreDownstream(txs)
            pipe.send(scoreUp if scoreUp > scoreDown else scoreDown)
            print(f"Calculated Score for {addr}")
            
        except Exception as e:
            print(f"Failed to calculate Score for {addr}:")
            print(traceback.format_exc())
            print("")
            pipe.send(0)

        
        
    def _riskScoreDownstream(self,txs) -> int:
        score = 0
        for tx in txs:
            _score = Risk_scoring.recursive_search(tx["txid"], 1, self.depth,0)
            if _score > score:
                score = _score
        return score
                
                
    def _riskScoreUpstream(self,txs) -> int:
        score = 0
        for tx in txs:
            _score = score = Risk_scoring_upstream.recursive_upstream_search(tx["txid"], 1, self.depth,0)
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
        
    
def main(args):
    print("____________TRANSACTION RISK SCORE____________")
    trs = TransactionRiskScore(args.depth)
    print("FINAL SCORE:"+str(trs.score(args.transaction)),flush=True);
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-tx', '--transaction',
                        help='Transaction hash', type=str, required = True)
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance (Default 2)', type=int, required = False, default = 2)
    args = parser.parse_args()
    main(args)