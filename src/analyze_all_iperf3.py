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

if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Parse experiments\' data.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to data folder')
    parser.add_argument('save_bad', type=str, help='path to save bad quality')
    parser.add_argument('save_table', type=str, help='path to save csv table')
    args = parser.parse_args()

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))

    row_counter = 0
    all_table = pd.DataFrame(
        index=range(len(conf.bandwidths) * len(conf.delays) * len(conf.jitters) * len(conf.losses)),
        columns=['bandwidth', 'delay', 'jitter', 'loss'] + conf.algorithms, 
    )
    # create iterator
    params = itertools.product(
        conf.bandwidths, conf.delays, conf.jitters, conf.losses
    )
    # run iteration for every quality combination
    for bw, delay, jitter, loss in params:
        all_table.iloc[row_counter] = [bw, delay, jitter, loss] + [0] * len(conf.algorithms)
        row_counter += 1

    all_counter = 0
    mad_counter = 0
    ignore_next = False

    # contains tuples of (alg, bw, delay, jitter, loss, mad)
    bad_list = []
    for alg in conf.algorithms:
        # create iterator
        params = itertools.product(
            conf.bandwidths, conf.delays, conf.jitters, conf.losses
        )
        # run iteration for every quality combination
        for bw, delay, jitter, loss in params:
            all_counter += 1
            quality = utils.Quality(bw, delay, jitter, loss)
            # gather speed values for different attempts 
            speed_lst = list()
            ut_list = list()
            delivered = 0
            time = 0
            view_lst = list()

            # get iperf3 server output path
            attempt = 0
            serv_fname = utils.get_srv_out_name(alg, quality, attempt)
            serv_path = os.path.join(args.data, serv_fname)
            try:
                mean_speed = utils.parse_server_out(serv_path)
            except Exception:
                print('failed to parse {}'.format(serv_fname))
                continue

            with open(serv_path, 'r') as fp:
                # ignore extra lines
                file_contents = ''
                for line in fp:
                    file_contents += line
                    if line == '}\n':
                        break
                # load iperf3 data
                data = json.loads(file_contents)

                all_table.loc[
                    (all_table['bandwidth'] == bw) \
                    & (all_table['delay'] == delay) \
                    & (all_table['jitter'] == jitter) \
                    & (all_table['loss'] == loss), \
                    alg
                ] = data['end']['sum_received']['bits_per_second'] / bw / 10**6 * 100
                
                # collect all intervals
                for interval in data['intervals']:
                    speed_lst.append(interval['sum']['bits_per_second'])
                    # sometimes there is number of zeroes and big value afterwards
                    if speed_lst[-1] / (bw * 10**4) < 0.00000000001:
                        ignore_next = True
                        continue
                    if speed_lst[-1] / (bw * 10**4) > 100 or ignore_next:
                        ignore_next = False
                        continue
                    delivered += interval['sum']['bytes']
                    time += interval['sum']['seconds']
                    ut_list.append(delivered * 8 / time / (bw * 10**4))
                sliced_lst = ut_list[0:]
                mad_val = mad(sliced_lst) / np.mean(sliced_lst)
                if mad_val > 0.15:
                    mad_counter += 1
                    bad_list.append((alg, bw, delay, jitter, loss, mad_val))
                    print('ALG {} B {} D {} J {} L {} MAD {}'.format(alg, bw, delay, jitter, loss, mad_val))

    with open(args.save_bad, 'w') as fp:
        for el in bad_list:
            fp.write('{}, {}, {}, {}, {}, {}\n'
                     .format(*el))
    print('failed {}/{}'.format(mad_counter, all_counter))

    with open(args.save_table, 'w') as fp:
        fp.write(all_table.to_csv())


