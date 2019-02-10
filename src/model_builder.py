#!/usr/bin/env python3

# Run like this:
# python3 model_builder.py data/conf.json ../../CAData/Data/ data/models

""" Generates decision trees for all algorithms
    Each tree estimates quality using socket statistics
"""

import argparse
import json
import itertools
import numpy as np
import os
import pickle
import utils
from sklearn import tree

from structures.config import Config
from utils import parse_view

if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Parse experiments\' data.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to data folder')
    parser.add_argument('res', type=str, help='path to save models')
    args = parser.parse_args()

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))

    # create directory to save data
    if not os.path.exists(args.res):
        os.makedirs(args.res)

    # create iterator
    params = itertools.product(
        conf.bandwidths, conf.delays, conf.jitters, conf.losses
    )

    # create result container
    samples = list()
    classes = list()

    # parse every file
    for alg in conf.algorithms:
        for bw, delay, jitter, loss in params:
            # gather speed values for different attempts 
            speed_lst = list()
            view_lst = list()
            for attempt in range(13):
                view_fname = 'net_{}_{}_{}_{}_{}_{}_view.txt'\
                             .format(alg, bw / 8, delay, delay * jitter / 100, loss, attempt)
                view_path = os.path.join(args.data, view_fname)
                if os.path.exists(view_path):
                    samples.append(utils.parse_view(view_path))
                    classes.append(str((bw, delay, jitter, loss)))

        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(samples, classes)

        model_fname = '{}.model'.format(alg)
        model_path = os.path.join(args.res, model_fname)
        with open(model_path, 'wb') as out:
            out.write(pickle.dumps(clf))
        print('classifier saved successfully: {}'.format(alg))