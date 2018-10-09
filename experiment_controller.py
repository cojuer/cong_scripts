#!/usr/bin/env python3

import argparse
import json
import itertools
import logging
import numpy as np
import os
import sys
import time

from config import Config

# TODO: move to the configuration file
attempts_number = 13

def read_iperf_srv_statistics(algorithm: str, bandwidth: int, delay: int,
                              jitter: int, loss: int, attempt: int) -> float:
    """ Gets speed from iperf server output
    """
    # TODO: non-hardcoded data directory
    with open('Data/net_{}_{}_{}_{}_{}_{}_server.json'
                .format(algorithm, bandwidth, delay, jitter, loss, attempt)) as fp:
        # iperf output isn't valid json, but its part is.
        # this correct part ends with '}\n' line.
        file_contents = ''
        for line in fp:
            file_contents += line
            if line == '}\n':
                break
        attempt_res = json.loads(file_contents)
        speed = attempt_res['end']['sum_received']['bits_per_second']
    return speed

def run_iteration(algorithm: str, bandwidth: int, delay: int,
                  jitter: int, loss: int, attempt: int) -> float:
    """ Runs experiment and returns collected speed
    """
    logging.info('attempt {} started'.format(attempt))
    
    # run scripts
    os.system('./test.sh -b')
    os.system('./test.sh -r {} {} {} {} {} {}'
              .format(bandwidth, delay, jitter, loss, algorithm, attempt))
    os.system('./test.sh -c')

    # read speed
    attempt_speed = read_iperf_srv_statistics(
        algorithm, bandwidth, delay, jitter, loss, attempt,
    )

    logging.info('attempt {} finished'.format(attempt))
    return attempt_speed


if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Run experiments for per algorithm statistics collection')
    parser.add_argument('--conf', type=str, default='data/conf.json', 
                        help='path to configuration file')
    parser.add_argument('--log', type=str, default='logs/alg_stats_collector.log',
                        help='path to write log')
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(filename=args.log, filemode='w', level=logging.INFO)

    # load configuration
    with open(args.conf, 'r') as fp:
        config = Config(json.load(fp))

    # create iterator
    params = itertools.product(config.algorithms, config.bandwidths, config.delays, 
                               config.jitters, config.losses)

    for alg, bw, delay, jitter, loss in params:
        logging.info('Test {} {} {} {} {} started'.format(alg, bw, delay, jitter, loss))
        speed_lst = list()
        for attempt_num in range(attempts_number):
            attempt_speed = run_iteration(
                algorithm=alg, bandwidth=bw/8, delay=delay,
                jitter=delay * jitter / 100, loss=loss, attempt=attempt_num,
            )
            speed_lst.append(attempt_speed)
            
            variance = np.std(speed_lst) / np.mean(speed_lst)
            logging.info('speed: {}'.format(attempt_speed))
            logging.info('variance: {}'.format(variance))

            # if variance is less than some number, we consider
            # speed estimation to be accurate enough
            # also border values are removed based on number of attempts
            if attempt_num >= 5:
                coeff = int((attempt_num - 5) / 2)
                if coeff == 0:
                    val = np.std(speed_lst) / np.mean(speed_lst)
                else:
                    final_list = sorted(speed_lst)[coeff:-coeff]
                    val = np.std(final_list) / np.mean(final_list)
                logging.info('variance+: {}'.format(val))
                if val < 0.005 or variance < 0.005:
                    logging.info('stopped at attempt {}'.format(attempt_num))
                    break
                    
        logging.info('Final mean: {}'.format(np.mean(speed_lst)))
        logging.info('Test {} {} {} {} {} finished'.format(alg, bw, delay, jitter, loss))

