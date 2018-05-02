#!/usr/bin/env python3

import argparse
import json
import itertools
import logging
import numpy as np
import os
import sys
import time
from . import utils

if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Run experiments.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to save data')
    parser.add_argument('models', type=str, help='path to models folder')
    parser.add_argument('optimal', type=str, help='path to optimal data')
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(filename='sample_full.log', filemode='w', level=logging.INFO)

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = json.load(fp)

    algs = conf['algorithm']
    bws = conf['bandwidth']
    delays = conf['delay']
    jitters = conf['jitter']
    losses = conf['loss']
    attempt_num = 13

    # read models
    models = {}
    for alg in algs:
        with open('model_{}'.format(alg), 'rb') as fp:
            models[alg] = pickle.load(fp)

    # read optimal algorithms
    optimals = {}
    with open(args.optimal, 'r') as fp:
        for line in fp:
            if len(line) == 0: 
                break
            a, b, c, d, e, f = line.split(' ')
            optimals[(float(a), float(b), float(c), float(d))] = f

    # create iterator
    params = itertools.product(algs, bws, delays, jitters, losses)

    for alg, bw, delay, jitter, loss in params:
        logging.info('Scenario {} {} {} {} {} started'.format(alg, bw, delay, jitter, loss))
        speed_lst = list()
        for i in range(attempt_num):
            logging.info('Attempt {} stage 1'.format(i))
            # run 1st stage
            os.system('./test.sh -b')
            os.system('./test.sh -r {} {} {} {} {} {}'.format(bw / 8, delay, delay * jitter / 100, loss, alg, i))
            os.system('./test.sh -c')

            # move data to new folder
            data_path = os.path.join(args.data, alg, 'from')
            os.system('mv Data/net_* {}'.format(data_path))
            
            # read socket data
            file_prefix = 'net_{}_{}_{}_{}_{}_{}_' \
                .format(alg, bw / 8, delay, delay * jitter / 100, loss, i))
            view_fname = prefix + 'view.txt'
            view_path = os.path.join(data_path, view_fname)
            sample = utils.parse_view(view_path)

            # retrieve predicted characteristics
            predicted_class = models[alg].predict(sample)
            pbw, pdelay, pjitter, ploss = predicted_class.split(',')

            # get optimal algorithm
            new_alg = optimals[(pbw, pdelay, pjitter, ploss)]

            logging.info('Attemps {} stage 2'.format(i))
            # run 2nd stage
            os.system('./test.sh -b')
            os.system('./test.sh -r {} {} {} {} {} {}'.format(bw / 8, delay, delay * jitter / 100, loss, new_alg, i))
            os.system('./test.sh -c')

            # move data to new folder
            data_path = os.path.join(args.data, alg, 'to')
            os.system('mv Data/net_* {}'.format(data_path))
