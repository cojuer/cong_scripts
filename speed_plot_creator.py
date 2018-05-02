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


def parse_view(file_path: str) -> (float, int):
    with open(file_path, 'r') as fp:
        content = fp.readlines()
        acks_num = int(content[1].split(':')[1])
        loss_num = int(content[2].split(':')[1])
        rtt = int(content[3].split(':')[1])
    return (1.0 * loss_num / acks_num, rtt)


if __name__ == "__main__":
    # run parser
    parser = argparse.ArgumentParser(description='Create speed plots for given algorithm')
    parser.add_argument('file', type=str, help='path to algorithm data')
    args = parser.parse_args()

    delay_data = dict()
    bw_data = dict()
    loss_data = dict()
    jitter_data = dict()
    
    with open(args.file, 'r') as in_a:
        for line in in_a:
            if len(line) == 0:
                break
            bw, delay, jitter, loss, speed, *f = line.split(' ')
            bw, delay, jitter, loss, speed = float(bw), float(delay), float(jitter), float(loss), float(speed)
            if bw not in bw_data:
                bw_data[bw] = list()
            if delay not in delay_data:
                delay_data[delay] = list()
            if jitter not in jitter_data:
                jitter_data[jitter] = list()
            if loss not in loss_data:
                loss_data[loss] = list()

            bw_data[bw].append(float(speed))
            delay_data[delay].append(float(speed))
            jitter_data[jitter].append(float(speed))
            loss_data[loss].append(float(speed))    

    delay_res = dict()
    bw_res = dict()
    loss_res = dict()
    jitter_res = dict()

    for key, value in delay_data.items():
        delay_res[key] = np.mean(value)
    for key, value in bw_data.items():
        bw_res[key] = np.mean(value)
    for key, value in jitter_data.items():
        jitter_res[key] = np.mean(value)
    for key, value in loss_data.items():
        loss_res[key] = np.mean(value)

    with open('res_test.txt', 'w') as fp:
        fp.write('delay\n')
        for key, value in sorted(delay_res.items()):
            fp.write('({}, {})\n'.format(key, value))
        fp.write('bandwidth\n')
        for key, value in sorted(bw_res.items()):
            fp.write('({}, {})\n'.format(key, value))
        fp.write('loss\n')
        for key, value in sorted(loss_res.items()):
            fp.write('({}, {})\n'.format(key, value))
        fp.write('jitter\n')
        for key, value in sorted(jitter_res.items()):
            fp.write('({}, {})\n'.format(key, value))