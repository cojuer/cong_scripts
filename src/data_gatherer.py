#!/usr/bin/env python3

import functools
import operator
import argparse
import json
import itertools
import logging
import numpy as np
import os

from utils import *
from structures.config import Config


def run_iteration(alg: str, quality: Quality, attempt: int, attempt_time: int) -> float:
    """ Runs experiment and returns collected speed
    """
    logging.info('attempt {} started'.format(attempt))

    tc_quality = quality.to_tc_quality()
    # run scripts
    os.system('./test.sh -b')
    os.system('./test.sh -r {} {} {} {} {} {}'
              .format(tc_quality.bandwidth, tc_quality.delay, 
                      tc_quality.jitter, tc_quality.loss, alg, attempt, attempt_time))
    os.system('./test.sh -c')

    logging.info('attempt {} finished'.format(attempt))


if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Run experiments for per algorithm statistics collection')
    parser.add_argument('savepath', type=str, help='path to save experiments data')
    parser.add_argument('--conf', type=str, default='data/conf.json',
                        help='path to configuration file')
    parser.add_argument('--log', type=str, default='logs/run_gather_data.log',
                        help='path to write log')
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(filename=args.log, filemode='w', level=logging.INFO)

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))
    attempt_time = conf.time

    # create directory to save data
    if not os.path.exists(args.savepath):
        os.makedirs(args.savepath)

    iters = [conf.algorithms, conf.bandwidths, conf.delays,
             conf.jitters, conf.losses]
    exp_num = functools.reduce(operator.mul, map(len, iters), 1)

    # create iterator
    params = itertools.product(conf.algorithms, conf.bandwidths, conf.delays,
                               conf.jitters, conf.losses)

    counter = 0
    for alg, bw, delay, jitter, loss in params:
        quality = Quality(bw, delay, jitter, loss)

        counter += 1
        logging.info('Test {}/{}: {} {} {} {} {} started'
                     .format(counter, exp_num, alg, bw, delay, jitter, loss))
        for attempt_num in range(conf.num_attempts):
            # run scripts
            run_iteration(alg, quality, attempt_num, attempt_time)

        logging.info('Test {}/{}: {} {} {} {} {} finished'
                     .format(counter, exp_num, alg, bw, delay, jitter, loss))
