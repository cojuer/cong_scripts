#!/usr/bin/env python3

import argparse
import json
import itertools
import logging
import numpy as np
import os
import sys
import time

if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Run experiments.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(filename='sample.log', filemode='w', level=logging.INFO)

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = json.load(fp)

    algs = conf['algorithm']
    bws = conf['bandwidth']
    delays = conf['delay']
    jitters = conf['jitter']
    losses = conf['loss']

    # create iterator
    params = itertools.product(algs, bws, delays, jitters, losses)

    for alg, bw, delay, jitter, loss in params:
        logging.info('Test {} {} {} {} {} started'.format(alg, bw, delay, jitter, loss))
        speed_lst = list()
        for i in range(13):
            logging.info('Attempt {}'.format(i))
            # run scripts
            os.system('./test.sh -b')
            os.system('./test.sh -r {} {} {} {} {} {}'.format(bw / 8, delay, delay * jitter / 100, loss, alg, i))
            os.system('./test.sh -c')

            # read speed
            with open('Data/net_{}_{}_{}_{}_{}_{}_server.json'
                      .format(alg, bw / 8, delay, delay * jitter / 100, loss, i)) as fp:
                file_contents = ''
                for line in fp:
                    file_contents += line
                    if line == '}\n':
                        break
                attempt_res = json.loads(file_contents)
                speed = attempt_res['end']['sum_received']['bits_per_second']
                speed_lst.append(speed)

            print(i, np.std(speed_lst) / np.mean(speed_lst))
            # check variance
            if i >= 5:
                coeff = int((i - 5) / 2)
                if coeff == 0:
                    val = np.std(speed_lst) / np.mean(speed_lst)
                else:
                    val = np.std(sorted(speed_lst)[coeff:-coeff]) / np.mean(sorted(speed_lst)[coeff:-coeff])
                print('sorted {}'.format(val))
                if val < 0.005:
                    print('stop at attempt {}'.format(i))
                    break
                    
        print('mean for {} {} {} {} {} is {}'.format(bw, delay, jitter, loss, alg, i, np.mean(speed_lst)))

        logging.info('Test {} {} {} {} {} finished'.format(alg, bw, delay, jitter, loss))
        print('Test {} {} {} {} {} finished'.format(alg, bw, delay, jitter, loss))

