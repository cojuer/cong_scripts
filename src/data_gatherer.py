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
        speed_lst = list()
        for attempt_num in range(conf.num_attempts):
            # run scripts
            run_iteration(alg, quality, attempt_num)

            # read speed
            filepath = os.path.join(args.savepath, 
                                    get_srv_out_name(alg, quality, attempt_num))
            attempt_speed = parse_server_out(filepath)
            speed_lst.append(attempt_speed)

            # allow stop if variance is low
            if attempt_num >= 5:
                # calculate variance
                variance = np.std(speed_lst) / np.mean(speed_lst)
                logging.info('speed: {}'.format(attempt_speed))
                logging.info('variance: {}'.format(variance))

                if variance < 0.005:
                    logging.info('stopped at attempt {}'.format(attempt_num))
                    break

        logging.info('Final mean: {}'.format(np.mean(speed_lst)))
        logging.info('Test {}/{}: {} {} {} {} {} finished'
                     .format(counter, exp_num, alg, bw, delay, jitter, loss))
