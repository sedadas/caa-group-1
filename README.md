# Project

Create the environment
```
conda env create -f env.yml
```

Activate the environment
```
conda activate caa_project_venv
```
Deactivate environment
```
conda deactivate
```
    
Example of running command for Neighborhood
```
python ./scripts/Neighborhood.py -f "./data/input_addresses.json" -d 1 -t "data/transactions.json" -nb 4 -s True
```

Example of running command for clustering
```
python ./scripts/clustering.py -o "data/clusters.json" -t "data/transactions.json"
```
Exemple of running command for risk scoring upstream
```
python ./Risk_scoring_upstream.py -d 4 -tx "c277a6c3d2c32b2c75ceebaca140b2e9ca9a31b32f464b64a4b11ab858b81708"
```

Exemple of running command for Transaction risk scoring 
```
python ./TransactionRiskScore.py -d 3 -tx "e377ac9333e4527fa86d4e096525f7ca81e9fd6212237d8601a0ccae916de23c"
```
## Scripts
### BitcoinAPI
Client to fetch data from blockstream using Esplora HTTP API.

### Risk scoring
Computes the local downstream score of a transaction by exploring transactions downstream with less than 10 outputs within the depth limit set. Takes the following arguments -d (depth) and -tx transaction

### Risk scoring upstream
Computes the local upstream score of a transaction by exploring transactions upstream within the depth limit set. Takes the following arguments -d (depth) and -tx transaction

### Transaction Risk score
Computes the transaction risk score by averaging particpants account score. Account score is the highest upstream/downstream score of the addresses 20 most recent transactions.

### DataMerge
This Scripts loads all tagpack yaml files, merges them into one file and saves it as data.csv\
It is needed to prepare the data for the TransactionRiskScore.\
You can configure it within config.yaml:\
config["paths"]["data"] is the output folder (where to save the data.csv)\
config["paths"]["tagpacks"] is the folder with the tagpack yaml files\

