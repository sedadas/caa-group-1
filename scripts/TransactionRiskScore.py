# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from multiprocessing.pool import ThreadPool

class TransactionRiskScore:
    api = BitcoinAPI()
    threadPool = None
    depth = 0
    
    def __init__(self,depth):
        self.depth = depth
        
    def score(self,tx):
        # For the Transaction, get its participants
        txDetails = self.api.getTransaction(tx)
        participants = self._getParticipants(txDetails)
        
        score = 0
        #Calculate the Risk score for all participants
        self.threadPool = ThreadPool(len(participants))
        for index, participant in enumerate(participants):
            print("("+str((index+1))+"/"+str(len(participants))+") Calculating Risk Score for account '"+participant+"'")
            async_result = self.threadPool.apply_async(self._accountRiskScore, (participant)) 
            score += async_result.get()
            
        #return average
        return score/len(participants)
        
    def _accountRiskScore(self,*addr):
        addr = ''.join(addr)
        return 12345 #TODO: call func to get score of the account address.
        
        
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
    print("FINAL SCORE:"+str(trs.score(args.transaction)));
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-tx', '--transaction',
                        help='Transaction hash', type=str, required = True)
    parser.add_argument('-d', '--depth',
                        help='Neighbors distance (Default 2)', type=int, required = False, default = 2)
    args = parser.parse_args()
    main(args)