# Project

## Scripts
### BitcoinAPI
Client to fetch data from blockstream using Esplora HTTP API.
### Neighborhood
This script uses networkx and pyvis.network to create a graph of neighbors for a set of bitcoin addresses.\
A Neighbor of an give address is a bitcoin address that had a transaction with the given address.
| Argument | Meaning                                                                                                                                                                                                                       | Example                           | Required           |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|--------------------|
| -f       | JSON File that includes the bitcoin addresses                                                                                                                                                                                 | -f "../data/input_addresses.json" | Yes                |
| -d       | In how many iterations would you like to fetch the neighbors of the neighbors. 1 = You only fetch the neighbors of the given bitcoin addresses. 2 = You fetch the neighors of the given bitcoin addresses and there neighbors | -d 1                              | No (default 1)     |
| -html    | Set this value if you like to get an graph. Name for the html file that shows the interactive created graph.                                                                                                                  | -html "graph.html"                | No                 |
| -json    | Set this value if you like to get the graph exported as json. Name for the json file that contains the exported created graph                                                                                                 | -json "graph.json"                | No                 |
| -t       | Set this value if you like to export a list of transactions that have been used to create this graph                                                                                                                          | -t "transactions.json"            | No                 |
| -max     | Since an bitcoin address can gave thousands of transactions, specifiy an limit. Due to the docs of blockstream api, it should be a multiple of 25                                                                             | -max 25                           | No (default 25)    |
| -pysics  | Enables the rendering of the graph                                                                                                                                                                                            | -physics false                    | No (default true)  |
| -jupyter | Set this to true if you face troubles using jupyter notebook                                                                                                                                                                  | -jupyter true                     | No (default false) |


### DataMerge
This Scripts loads all tagpack yaml files, merges them into one file and saves it as data.csv\
You can configure it within config.yaml:\
config["paths"]["data"] is the output folder (where to save the data.csv)\
config["paths"]["tagpacks"] is the folder with the tagpack yaml files\

