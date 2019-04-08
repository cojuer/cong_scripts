#!/usr/bin/env python3

import functools
import operator
import argparse
import json
import itertools
import logging
import numpy as np
import os
from subprocess import Popen, TimeoutExpired

from utils import *
from structures.config import Config

""" Run experiment and:
    - collect iperf3 client and server output;
    - collect final statistics from kernel tool;
    - collect log entries written by kernel tool;
"""


def run_iteration(alg: str, quality: Quality, attempt: int) -> float:
    """ Runs experiment and returns collected speed
    """
    logging.info('attempt {} started'.format(attempt))

    tc_quality = quality.to_tc_quality()
    # run scripts
    os.system('./test.sh -b')
    os.system('./test.sh -r {} {} {} {} {} {}'
              .format(tc_quality.bandwidth, tc_quality.delay, 
                      tc_quality.jitter, tc_quality.loss, alg, attempt))
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
            # check whether experiment was done before
            log_path = os.path.join(args.savepath, 
                                    get_log_name(alg, quality, attempt_num))
            if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
                continue

            # run log converter
            p = Popen([
                'sudo', 'python3.7', 'log_converter.py', '/var/log/kern.log',
                os.path.join(args.savepath, get_log_name(alg, quality, attempt_num))
            ])
            
            # run scripts
            run_iteration(alg, quality, attempt_num)

            # wait for log to stop
            try:
                p.wait(timeout=10)
            except TimeoutExpired:
                logging.info('error reading log: {}/{}: {} {} {} {} {}'
                             .format(counter, exp_num, alg, bw, delay, jitter, loss))

        logging.info('Test {}/{}: {} {} {} {} {} finished'
                     .format(counter, exp_num, alg, bw, delay, jitter, loss))
