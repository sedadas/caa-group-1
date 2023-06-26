# -*- coding: utf-8 -*-
import requests
import json
import multiprocessing
from joblib import Parallel, delayed

class BitcoinAPI:
    BASE_URL = 'https://blockstream.info/api/'
    
    def getTransactions(self,address,maxTransactions):
        return self._get_address_txs_Retry(address, False, maxTransactions)
    

    def getTransaction(self,tx):
       url = self.BASE_URL + 'tx/' + str(tx)
       r = requests.get(url)
       if(r.status_code == 200):
           return json.loads(r.text)
       else:
           print("An Error occured trying to fetch transaction '"+str(tx)+"' (HTTP STATUS "+r.status_code+")")
           return "";
        
        
    def _get_address_txs_Retry(self,address, retry, maxTransactions):
        if(retry == True):
            print("Trying again...")
            
        url = self.BASE_URL + 'address/' + str(address) + "/txs"
        r = requests.get(url)
        txs = []
        
        if(r.status_code == 200):
            response = json.loads(r.text)
            txs += response
        else:
            print("Failed to get '"+str(url)+"', HTTP response is "+str(r.status_code))
            if(retry == False):
                return self._get_address_txs_Retry(address,True)
            return

        num_cores = multiprocessing.cpu_count()
        txs += Parallel(n_jobs=num_cores, prefer="threads")(delayed(self._get_single_address_tx)(address, txs, retry) for i in range(maxTransactions))
        res = [x for x in txs if x]
        return res

        
    def _get_single_address_tx(self, address, txs, retry):
        url = self.BASE_URL + 'address/' + str(address) + "/txs/chain/"+ txs[-1]['txid']
        r = requests.get(url)
        if(r.status_code == 200):
            response = json.loads(r.text)
            if isinstance(response, list) and len(response) != 0:
                return response[0]
            return response
        else:
            print("Failed to get '"+str(url)+"', HTTP response is "+str(r.status_code))
            if retry:
                return self._get_single_tx(address, txs, retry)
            return


    def __str__(self):
        return self.BASE_URL
    
