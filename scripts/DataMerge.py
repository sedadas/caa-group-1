# -*- coding: utf-8 -*-


#   
#   Use this script to merge all (tagpack) yaml files into one .csv file
#   Input folder: config["paths"]["tagpacks"]
#   Output folder: config["paths"]["data"]
#

from argparse import ArgumentParser
import modin.pandas as pd
import json
import yaml
import os
import numpy as np
import ray


with open('../config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


def main(args):
    startedRay = False
    if not ray.is_initialized():
        startedRay = True
        ray.init()
        
    data = loadData()
    data = data.query("currency == 'BTC'")
    
    
    data["address"] = data["tags"].apply(lambda x: x["address"],axis=1)
    data = data.drop(["creator","is_cluster_definer","confidence","description","currency","label","lastmod","source","actor","abuse","tags"], axis=1)
    data.to_csv(config["paths"]["data"]+"/data.csv",index=False)
    
    print("Created "+config["paths"]["data"]+"/data.csv")
    if startedRay:
        ray.shutdown()
    #data.to_csv(config["paths"]["data"]+"/"+ (args.output or "data.csv"))
    #print("Created "+config["paths"]["data"]+"/"+ (args.output or "data.csv"))


def loadData():
    files = np.array(os.listdir(config["paths"]["tagpacks"]))
    dataSets = map(loadYamlAsPandasDataFrame,map(lambda x: config["paths"]["tagpacks"]+"/"+x,files))
    return pd.concat(dataSets)


def loadYamlAsPandasDataFrame(file):
    print("Loading "+file)
    with open(file, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        return pd.DataFrame.from_dict(data)
    

if __name__ == '__main__':
    if config["paths"]["tagpacks"] is None:
        print("Please set tagpacks path in config.yaml")
    if config["paths"]["data"] is None:
            print("Please set data path in config.yaml")
        
    else:
        parser = ArgumentParser()
        #parser.add_argument('-o', '--output',
        #                    help='Output file (e.g. "data.csv")', type=str, required=False)
        args = parser.parse_args()
        main(args)
        
    