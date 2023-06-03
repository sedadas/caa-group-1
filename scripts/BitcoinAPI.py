# -*- coding: utf-8 -*-
import requests
import json

class BitcoinAPI:
    BASE_URL = 'https://blockstream.info/api/'
    
    def getTransactions(self,address):
        url = self.BASE_URL + 'address/' + str(address) + "/txs"
        r = requests.get(url)
        if(r.status_code == 200):
            return json.loads(r.text)
        else:
            print("Failed to get '"+str(url)+"', HTTP response is "+str(r.status_code))
            return None;
        
    
    def __str__(self):
        return self.BASE_URL
    