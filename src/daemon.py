#!/usr/bin/env python3

import os
import argparse
import time
import json
import typing
import daemon
import logging
import pickle
import subprocess

from utils import parse_res, Quality

LOG = logging.getLogger(__file__)


def run_iteration(kern_log, sleep_time, optimals):
    time_start = time.time()

    # get statistics
    # get_cmd = ['congdb-ctl', 'get-entry', '{}'.format(str(rule_id))]
    # result = subprocess.run(get_cmd, stdout=subprocess.PIPE)
    # sample = parse_ctl_output(result.output)

    # read kernel log
    where = kern_log.tell()
    line = kern_log.readline()

    # sleep if nothing to read
    if not line:
        time_end = time.time()
        delta = time_end - time_start
        time.sleep(sleep_time - delta)

        kern_log.seek(where)
        return

    # check for line of interest
    n_index = line.find('notify!')
    if n_index == -1:
        return

    # get statistics from kernel log
    _, src_ip, dst_ip, rtt, loss_num, acks_num = \
        [word.strip() for word in line[n_index:].split(' ')] 
    rtt, loss_num, acks_num = int(rtt), int(loss_num), int(acks_num)

    # ignore service traffic with exactly 8 acks
    if acks_num == 0 or acks_num == 8 or (src_ip, dst_ip) not in interfaces:
        return

    # classify characteristics
    sample = (1.0 * loss_num / acks_num, rtt)
    predicted_class = models[alg].predict([sample])
    pbw, pdelay, pjitter, ploss = predicted_class[0][1:-1].split(',')
    pquality = Quality(pbw, pdelay, pjitter, ploss)

    # choose new algorithm
    new_alg = optimals[pquality]
    print(pquality, new_alg)

    # print('going to set algorithm {} for quality: {} {} {} {}'
    #       .format(new_alg, pbw, pdelay, pjitter, ploss))
    # update kernel
    # get_cmd = ['congdb-ctl', 'set-entry', 
    #            '{}'.format(str(rule_id)), alg]
    # result = subprocess.run(get_cmd, stdout=subprocess.PIPE)
    # assert result.returncode == 0


def run(kern_log, models, sleep_time, optimals):
    while True:
        run_iteration(kern_log, sleep_time, optimals)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run TCP improvement daemon')
    parser.add_argument('conf', type=str, help='path to configuration file')
    parser.add_argument('models', type=str, help='path to models folder')
    parser.add_argument('optimals', type=str, help='path to csv with optimal algorirhms per quality')
    parser.add_argument('--kern_log', type=str, default='/var/log/kern.log', help='path to read kernel log')
    parser.add_argument('--log', type=str, default='logs/daemon.log', help='path to write log')
    cmd_args = parser.parse_args()

    # read configuration
    with open(cmd_args.conf, 'r') as fp:
        conf = json.load(fp)

    algorithms = conf['algorithms']
    interfaces = [(intf['src'], intf['dst']) for intf in conf['interfaces']]
    sleep_time = conf['sleep_time']

    # read models
    models = dict()
    for alg in algorithms:
        model_path = os.path.join(cmd_args.models, '{}.model'.format(alg))
        with open(model_path, 'rb') as fp:
            models[alg] = pickle.load(fp)

    # read optimal algorithms per quality
    optimals_path = os.path.join(cmd_args.optimals, 'optimals.csv')
    optimals = parse_res(optimals_path)

    # with daemon.DaemonContext(), open(cmd_args.in_log, 'r') as kern_log:
    with open(cmd_args.kern_log, 'r') as kern_log:
        run(kern_log, models, sleep_time, optimals)