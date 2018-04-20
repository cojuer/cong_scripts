#!/usr/bin/env python3

import argparse
import json
import itertools
import numpy as np
import os

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


if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Parse experiments\' data.')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('data', type=str, help='path to data folder')
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
    # (bw, delay, jitter, loss) -> (alg, speed)
    result = dict()
    per_alg_res = dict()
    for alg in algs:
        per_alg_res[alg] = dict()

    # parse every file
    counter = 0
    for bw, delay, jitter, loss in params:
        for alg in algs:
            # gather speed values for different attempts 
            speed_lst = list()
            for attempt in range(13):
                file_name = 'net_{}_{}_{}_{}_{}_{}_server.json'\
                    .format(alg, bw / 8, delay, delay * jitter / 100, loss, attempt)
                file_path = os.path.join(args.data, file_name)
                if os.path.exists(file_path):
                    counter += 1
                    speed_lst.append(parse_server_out(file_path))
            # update result if speed is max
            key = (bw, delay, jitter, loss)
            if len(speed_lst) == 0:
                print('error: {} {}'.format((bw, delay, jitter, loss), alg))
            else:
                per_alg_res[alg][key] = np.mean(speed_lst)
                if key in result:
                    if np.mean(speed_lst) > result[key][0]:
                        result[key] = (np.mean(speed_lst), alg)
                else:
                    result[key] = (np.mean(speed_lst), alg)
            print(counter)

    # save result to file
    with open('res.txt', 'w') as out:
        for key, value in result.items():
            out.write('{} {} {} {} {} {}\n'.format(key[0], key[1], key[2], key[3], value[0], value[1]))

    for alg in algs:
        with open('res_{}.txt'.format(alg), 'w') as out:
            for key, value in per_alg_res[alg].items():
                out.write('{} {} {} {} {}\n'.format(key[0], key[1], key[2], key[3], value))


