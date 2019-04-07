#!/usr/bin/env python3.7

""" Read TCP statistics (produced by kernel module) 
    from kernel log and save it to specified path. 
"""

import argparse
import json
import itertools
import os
import sys
import time
from src import utils

def main():
    # run parser
    parser = argparse.ArgumentParser(description='Convert log to another form.')
    parser.add_argument('log', type=str, help='path to kernel log')
    parser.add_argument('save', type=str, help='path to save converted data')
    args = parser.parse_args()

    with open(args.log, 'r') as kern_log, open(args.save, 'w') as out:
        # move to the end of log file (ignore existing data)
        kern_log.seek(0, 2)
        while True:
            # move through log
            where = kern_log.tell()
            line = kern_log.readline()

            # sleep if nothing to read
            if not line:
                time.sleep(1)
                kern_log.seek(where)
                continue

            # check whether socket released
            release_idx = line.find('release experiment socket')
            if release_idx != -1:
                print('socket released')
                return

            # check for line of interest
            collect_idx = line.find('collect:')
            if collect_idx == -1:
                continue

            # get statistics from kernel log
            # ignore lots of useless words which make reading log simple
            _1, ip_src, _2, ip_dst, _3, log_rtt, _4, log_retr, _5, log_delv, _6, log_time = \
                [word.strip() for word in line[collect_idx:].split()]
            
            # ignore iperf3 service flows
            # 10.0.0.1 and 10.0.0.2 are used for experiments
            if not ip_src == '10.0.0.1' or not ip_dst == '10.0.0.2':
                continue
            
            log_rtt, log_retr, log_delv, log_time = \
                int(log_rtt), int(log_retr), int(log_delv), int(log_time)
            
            # save values to file
            out.write('{}, {}, {}, {}\n'.format(log_rtt, log_retr, log_delv, log_time))


if __name__ == "__main__":
    main()