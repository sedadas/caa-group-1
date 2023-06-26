# -*- coding: utf-8 -*-
import requests
import json

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
                return self._get_address_txs_Retry(address,True,maxTransactions)
            return []
        
        while(len(response) > 0 and len(txs) < maxTransactions):
            url = self.BASE_URL + 'address/' + str(address) + "/txs/chain/"+ response[-1]['txid']
            r = requests.get(url)
            if(r.status_code == 200):
                response = json.loads(r.text)
                txs += response
            else:
                print("Failed to get '"+str(url)+"', HTTP response is "+str(r.status_code))
                if(retry == False):
                    return self._get_address_txs_Retry(address,True,maxTransactions)
                return []
    
        if(retry == True):
            print("Retry was successful")

        return txs
        
    
    def __str__(self):
        return self.BASE_URL
    