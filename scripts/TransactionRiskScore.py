# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from BitcoinAPI import BitcoinAPI
from multiprocessing import Process, Pipe

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
        for index, participant in enumerate(participants):
            print("("+str((index+1))+"/"+str(len(participants))+") Calculating Risk Score for account '"+participant+"'")
            parent_conn, child_conn = Pipe()
            process = Process(target=self._accountRiskScore,args=(child_conn,participant))
            process.start()
            score += parent_conn.recv()
            process.join()
            
        #return average
        return score/len(participants)
        
    def _accountRiskScore(self,pipe,*addr):
        addr = ''.join(addr)
        pipe.send(12345) #TODO: call func to get score of the account address.
        pipe.close()
        
        
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