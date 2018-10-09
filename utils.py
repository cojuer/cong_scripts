#!/usr/bin/env python3

import json

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


def parse_res(file_path: str) -> dict():
    res = dict()
    with open(file_path, 'r') as fp:
        for line in fp:
            if len(line) == 0: 
                break
            a, b, c, d, e, f = line[:-1].split(' ')
            res[(float(a), float(b), float(c), float(d))] = f
    return res


def parse_res_per_alg(file_path: str) -> dict():
    res = dict()
    with open(file_path, 'r') as fp:
        for line in fp:
            if len(line) == 0: 
                break
            a, b, c, d, e = line[:-1].split(' ')
            res[(float(a), float(b), float(c), float(d))] = e
    return res