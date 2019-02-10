#!/usr/bin/env python3.7

# Run like this:
# python3 data_parser.py data/conf.json data/csv_data/ data/csv_results 

""" Script converts csv experiments data to following formats:
    1. Algorithm data: quality, speed (as csv)
    2. Best algorithms: quality, speed, algorithm (as csv)
    where quality is represented by:
    bandwidth | Mbit
    delay     | s
    jitter    | %
    loss      | %
"""

import argparse
import json
import itertools
import numpy as np
import os
from dataclasses import dataclass

from utils import *
from structures.config import Config

@dataclass
class BestAlgInfo:
    name: str
    speed: float


if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Convert csv data to algorithms\' average and best results')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to folder with csv data')
    parser.add_argument('res', type=str, help='path to save converted data')
    args = parser.parse_args()

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))

    # create directory to save data
    if not os.path.exists(args.res):
        os.makedirs(args.res)

    # quality -> (algorithm, speed)
    quality_to_best = dict()

    # parse every file
    for alg in conf.algorithms:
        alg_data = dict()

        with open(os.path.join(args.data, alg + '.csv')) as fp:
            for line in fp:
                bw, delay, jitter, loss, speed = line.split(',')
                quality = Quality(bw, delay, jitter, loss)
                speed = float(speed)

                # update result if speed is max
                if quality not in alg_data:
                    alg_data[quality] = list()
                alg_data[quality].append(speed)

            # save results per algorithm
            with open(os.path.join(args.res, 'res_{}.csv'.format(alg)), 'w') as out:
                for quality, speed_lst in sorted(alg_data.items()):
                    average_speed = np.mean(speed_lst)
                    out.write('{}, {}, {}, {}, {}\n'
                              .format(quality.bandwidth, quality.delay, 
                                      quality.jitter, quality.loss, average_speed))

            # populate optimals (best speed/algorithm for quality)
            for quality, speed_lst in sorted(alg_data.items()):
                average_speed = np.mean(speed_lst)
                if not quality in quality_to_best:
                    quality_to_best[quality] = BestAlgInfo(name=alg, speed=average_speed)
                if quality in quality_to_best and average_speed > quality_to_best[quality].speed:
                    quality_to_best[quality] = BestAlgInfo(name=alg, speed=average_speed)

    # save optimal speeds and algorithms per quality
    with open(os.path.join(args.res, 'optimals.csv'), 'w') as out:
        for quality, alg_info in sorted(quality_to_best.items()):
            out.write('{}, {}, {}, {}, {}, {}\n'
                      .format(quality.bandwidth, quality.delay, 
                              quality.jitter, quality.loss, alg_info.speed, alg_info.name))
