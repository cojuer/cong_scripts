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
    parser = argparse.ArgumentParser(description='Compare experiments\' data.')
    parser.add_argument('file_a', type=str, help='file to compare')
    parser.add_argument('file_b', type=str, help='file to compare')
    args = parser.parse_args()

    a_data = dict() 
    with open(args.file_a, 'r') as in_a:
        for line in in_a:
            if len(line) == 0:
                break
            a, b, c, d, e, *f = line.split(' ')
            a_data[(float(a), float(b), float(c), float(d))] = float(e)

    b_data = dict()
    with open(args.file_b, 'r') as in_b:
        for line in in_b:
            if len(line) == 0: 
                break
            a, b, c, d, e, *f = line
            a, b, c, d, e, *f = line.split(' ')
            b_data[(float(a), float(b), float(c), float(d))] = float(e)

    comp_list = list()
    for key, value in a_data.items():
        if key in b_data.keys():
            comp_list.append( (a_data[key] - b_data[key]) / (key[0] * 1000000) )

    print(comp_list)
    print(np.mean(comp_list))