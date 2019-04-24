#!/usr/bin/env python3

import argparse
import json
import itertools
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import utils

from structures.config import Config

def create_speed_plot(algs: list(), res: dict(), bwjl: () = '', folder: str = './') -> str:
    plots = ''
    keys, vals = {}, {}
    for alg in algs:
        keys[alg] = []
        vals[alg] = []
    for alg in algs:
        for key, val in sorted(res[alg].items()):
            keys[alg].append(key)
            vals[alg].append(val)
    for alg in algs:
        plt.plot(keys[alg], vals[alg], label=alg)
    if bwjl == 'l' or bwjl == 'b':
        plt.xscale("log")
    plt.legend(loc='upper right')
    plt.savefig(os.path.join(folder, '{}.png'.format(bwjl)))
    plt.close()


if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Create speed plots for given algorithms')
    parser.add_argument('conf', type=str, help='configuration file')
    parser.add_argument('table', type=str, help='path to utilization table')
    parser.add_argument('savedir', type=str, help='path to save plots')
    args = parser.parse_args()

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = Config(json.load(fp))

    # load utilization table
    table = pd.read_csv(args.table)

    algs = conf.algorithms

    # d - delay, b - bandwidth, j - jitter, l - loss
    # data is: alg <-> b <-> utilization list
    d_data = dict()
    b_data = dict()
    l_data = dict()
    j_data = dict()
    
    # d - delay, b - bandwidth, j - jitter, l - loss
    # res is: alg <-> b <-> mean utilization
    d_res = dict()
    b_res = dict()
    l_res = dict()
    j_res = dict()

    for alg in algs:
        d_data[alg] = dict()
        b_data[alg] = dict()
        l_data[alg] = dict()
        j_data[alg] = dict()
        # collect data values
        for idx, row in table.iterrows():
            b = row['bandwidth']
            d = row['delay']
            j = row['jitter']
            l = row['loss']

            if b not in b_data[alg]:
                b_data[alg][b] = list()
            if d not in d_data[alg]:
                d_data[alg][d] = list()
            if j not in j_data[alg]:
                j_data[alg][j] = list()
            if l not in l_data[alg]:
                l_data[alg][l] = list()
            
            utilization = row[alg]
            b_data[alg][b].append(utilization)
            d_data[alg][d].append(utilization)
            j_data[alg][j].append(utilization)
            l_data[alg][l].append(utilization)
 
        d_res[alg] = dict()
        b_res[alg] = dict()
        l_res[alg] = dict()
        j_res[alg] = dict()

        # collect res values
        for b, ut_list in b_data[alg].items():
            b_res[alg][b] = np.mean(ut_list)
        for d, ut_list in d_data[alg].items():
            d_res[alg][d] = np.mean(ut_list)
        for j, ut_list in j_data[alg].items():
            j_res[alg][j] = np.mean(ut_list)
        for l, ut_list in l_data[alg].items():
            l_res[alg][l] = np.mean(ut_list)

    create_speed_plot(algs, d_res, 'd', args.savedir)
    create_speed_plot(algs, b_res, 'b', args.savedir)
    create_speed_plot(algs, l_res, 'l', args.savedir)
    create_speed_plot(algs, j_res, 'j', args.savedir)

    sys.exit()

    lots_of_data = dict()
    lots_of_res = dict()
    
    for alg in algs:
        delay_data[alg] = dict()
        bw_data[alg] = dict()
        loss_data[alg] = dict()
        jitter_data[alg] = dict()

        path = os.path.join(args.results, 'res_{}.txt'.format(alg))
        with open(path, 'r') as in_a:
            for line in in_a:
                if len(line) == 0:
                    break
                bw, delay, jitter, loss, speed, *f = line.split(' ')
                bw, delay, jitter, loss, speed = float(bw), float(delay), float(jitter), float(loss), float(speed)

                if not (bw, jitter, loss) in lots_of_data:
                    lots_of_data[(bw, jitter, loss)] = dict()
                if not alg in lots_of_data[(bw, jitter, loss)]:
                    lots_of_data[(bw, jitter, loss)][alg] = dict()
                if not delay in lots_of_data[(bw, jitter, loss)][alg]:
                    lots_of_data[(bw, jitter, loss)][alg][delay] = list()
                lots_of_data[(bw, jitter, loss)][alg][delay].append(float(speed) / bw / 10**6)

        for bwjl, value in lots_of_data.items():
            if not bwjl in lots_of_res:
                lots_of_res[bwjl] = dict()
            if not alg in lots_of_res[bwjl]:
                lots_of_res[bwjl][alg] = dict()
            for key, data in lots_of_data[bwjl][alg].items():
                lots_of_res[bwjl][alg][key] = np.mean(data)

        for bwjl, value in sorted(lots_of_res.items()):
            fp.write(create_speed_plot(algs, value, bwjl))