#!/usr/bin/env python3.7

# Run like this:
# python3 data_converter.py data/conf.json ../../CAData/Data/ data/csv_data/ 

""" Script converts experiments data to csv with following format:
    bandwidth | Mbit
    delay     | s
    jitter    | %
    loss      | %
    speed     | Mbit
"""

import argparse
import csv
import sys
import json
import itertools
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from utils import *
from structures.config import Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert experiments data to csv format')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to folder with expertiments data')
    parser.add_argument('res', type=str, help='path to save converted data')
    args = parser.parse_args()

    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))

    # create directory to save data
    if not os.path.exists(args.res):
        os.makedirs(args.res)

    # parse every file
    for alg in conf.algorithms:
        alg_data = dict()

        # create quality iterator
        params = itertools.product(
            conf.bandwidths, conf.delays, conf.jitters, conf.losses
        )
        for quality_tuple in params:
            quality = Quality(*quality_tuple)
            speed_lst = list()
            # gather speed values for different attempts 
            for attempt in range(conf.num_attempts):
                # TODO: rework move from one quality format to another
                file_name = get_srv_out_name(alg, quality, attempt)
                file_path = os.path.join(args.data, file_name)
                if os.path.exists(file_path):
                    speed_lst.append(parse_server_out(file_path))
                else:
                    print('file does not exists: "{}"'.format(file_path))
            alg_data[quality] = speed_lst

        # save optimal speeds and algorithms per quality
        with open(os.path.join(args.res, alg + '.csv'), 'w') as out:
            for quality, speed_lst in sorted(alg_data.items()):
                for speed in speed_lst:
                    out.write('{}, {}, {}, {}, {}\n'
                              .format(quality.bandwidth, quality.delay, 
                                      quality.jitter, quality.loss, speed))
