#!/usr/bin/env python3

""" Generates efficiency table (.csv) from experiments data.
"""

import argparse
import json
import itertools
import scipy
import os
import sys
import pickle
import copy
import numpy as np
import pandas as pd
from sklearn import tree
from scipy.stats import variation

import utils
from structures.config import Config
from utils import parse_view

def mad(data, axis=None):
    return np.mean(np.absolute(data - np.mean(data, axis)), axis)

def best_alg(alg_to_value):
    """ Get alg with best utilization from dict alg<->ut
    """
    return max(alg_to_value.keys(), key=(lambda key: alg_to_value[key]))

def best_ut(alg_to_value):
    """ Get best utilization from dict alg<->ut
    """
    return max(alg_to_value.values())

def count_occ(word_list, word):
    """ Count number of occurences of given word in list of words
    """
    counter = 0
    for tmp_word in word_list:
        if tmp_word == word:
            counter += 1
    return counter

if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Parse experiments\' data.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('table', type=str, help='path to csv table')
    args = parser.parse_args()

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))

    table = pd.read_csv(args.table)
    # two new columns: best_alg and best_bw
    table['best_alg'] = table.apply(lambda row: best_alg({alg: row[alg] for alg in conf.algorithms}), axis=1)
    table['best_ut'] = table.apply(lambda row: best_ut({alg: row[alg] for alg in conf.algorithms}), axis=1)
    
    print('alg, average, max, best_num')
    for alg in conf.algorithms:
        ut_diff = table['best_ut'] - table[alg]
        best_algs = table['best_alg']
        print('{}, {}, {}, {}'
              .format(alg, np.average(ut_diff), np.max(ut_diff), count_occ(best_algs, alg)))
