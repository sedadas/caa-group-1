# Project

	conda env create -f env.yml

Activate the environment
	conda activate caa_project_venv
Deactivate environnement
	conda deactivate
    
Example of running command for Neighborhood
python ./scripts/Neighborhood.py -f "./data/input_addresses.json" -d 1 -t "data/transactions.json" -nb 4 -s True

Example of running command for clustering
python ./scripts/clustering.py -o "data/clusters.json" -t "data/transactions.json"