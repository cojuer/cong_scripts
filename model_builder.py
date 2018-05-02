#!/usr/bin/env python3

import argparse
import json
import itertools
import numpy as np
import os
import pickle
from sklearn import tree

def parse_server_out(file_path: str) -> int:
    with open(file_path, 'r') as fp:
        file_contents = ''
        for line in fp:
            file_contents += line
            if line == '}\n':
                break
        attempt_res = json.loads(file_contents)
        speed = attempt_res['end']['sum_received']['bits_per_second']
    return speed

def parse_view(file_path: str) -> (float, int):
    with open(file_path, 'r') as fp:
        content = fp.readlines()
        acks_num = int(content[1].split(':')[1])
        loss_num = int(content[2].split(':')[1])
        rtt = int(content[3].split(':')[1])
    return (1.0 * loss_num / acks_num, rtt)

if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Parse experiments\' data.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to data folder')
    parser.add_argument('models', type=str, help='path to models folder')
    args = parser.parse_args()

    # load configuration
    with open(args.conf, 'r') as fp:
        conf = json.load(fp)

    algs = conf['algorithm']
    bws = conf['bandwidth']
    delays = conf['delay']
    jitters = conf['jitter']
    losses = conf['loss']

    # create iterator
    params = itertools.product(bws, delays, jitters, losses)

    # create result container
    samples = list()
    classes = list()

    for alg in algs:
    # parse every file
        for bw, delay, jitter, loss in params:
            # gather speed values for different attempts 
            speed_lst = list()
            view_lst = list()
            for attempt in range(13):
                view_fname = 'net_{}_{}_{}_{}_{}_{}_view.txt'\
                    .format(alg, bw / 8, delay, delay * jitter / 100, loss, attempt)
                view_path = os.path.join(args.data, view_fname)
                if os.path.exists(view_path):
                    samples.append(parse_view(view_path))
                    classes.append(str((bw, delay, jitter, loss)))

        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(samples, classes)

        model_fname = 'model_{}.txt'.format(alg)
        model_path = os.path.join(args.models, model_fname)
        with open(model_path, 'wb') as out:
            out.write(pickle.dumps(clf))
        print('{} classifier saved successfully'.format(alg))