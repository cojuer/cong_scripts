#!/usr/bin/env python3

import json
from dataclasses import dataclass

@dataclass
class TcQuality:
    bandwidth: float
    delay: int
    jitter: float
    loss: float

    def __post_init__(self):
        self.bandwidth = float(self.bandwidth)
        self.delay = int(self.delay)
        self.jitter = float(self.jitter)
        self.loss = float(self.loss)

    def to_tuple(self) -> tuple:
        return self.bandwidth, self.delay, self.jitter, self.loss

@dataclass
class Quality:
    bandwidth: float
    delay: float
    jitter: float
    loss: float

    def __post_init__(self):
        self.bandwidth = float(self.bandwidth)
        self.delay = float(self.delay)
        self.jitter = float(self.jitter)
        self.loss = float(self.loss)

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, rhs):
        return self.to_tuple() < rhs.to_tuple()

    def __eq__(self, rhs):
        return (self.bandwidth, self.delay, self.jitter, self.loss) == \
            (rhs.bandwidth, rhs.delay, rhs.jitter, rhs.loss)

    def to_tc_quality(self) -> TcQuality:
        return TcQuality(self.bandwidth / 8, self.delay, 
                         self.delay * self.jitter / 100, self.loss)

    @staticmethod
    def from_tc_quality(tc_quality: TcQuality) -> 'Quality':
        return Quality(
            bandwidth = tc_quality.bandwidth * 8,
            delay = tc_quality.delay,
            jitter = tc_quality.jitter / tc_quality.delay * 100,
            loss = tc_quality.loss
        )

    def to_tuple(self) -> tuple:
        return self.bandwidth, self.delay, self.jitter, self.loss

def parse_server_out(file_path: str) -> int:
    """ Opens iperf server output and reads bits_per_second 
    """
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
    """ Probably parses CLI output with socket statistics
    """
    with open(file_path, 'r') as fp:
        content = fp.readlines()
        acks_num = int(content[1].split(':')[1])
        loss_num = int(content[2].split(':')[1])
        rtt = int(content[3].split(':')[1])
    return (1.0 * loss_num / acks_num, rtt)


def parse_res(file_path: str) -> dict:
    """ Opens file with optimal algorithms, parses 
        and returns data per quality characteristics
    """
    res = dict()
    with open(file_path, 'r') as fp:
        for line in fp:
            if len(line) == 0: 
                break
            bw, delay, jitter, loss, _, alg = \
                [elem.strip() for elem in line[:-1].split(',')]
            quality = Quality(bw, delay, jitter, loss)
            res[quality] = alg
    return res


def parse_res_per_alg(file_path: str) -> dict:
    """ Opens file with algorithm performance per quality, parses
        and returns data per quality charateristics
    """
    res = dict()
    with open(file_path, 'r') as fp:
        for line in fp:
            if len(line) == 0: 
                break
            bw, delay, jitter, loss, speed = \
                [elem.strip() for elem in line[:-1].split(',')]
            quality = Quality(bw, delay, jitter, loss)
            res[quality] = float(speed)
    return res

def get_srv_out_name(alg: str, quality: Quality, attempt: int) -> str:
    assert isinstance(quality, Quality)
    bw, delay, jitter, loss = quality.to_tc_quality().to_tuple()
    return 'net_{}_{}_{}_{}_{}_{}_server.json'\
        .format(alg, bw, delay, jitter, loss, attempt)

def get_log_name(alg: str, quality: Quality, attempt: int) -> str:
    assert isinstance(quality, Quality)
    bw, delay, jitter, loss = quality.to_tc_quality().to_tuple()
    return 'net_{}_{}_{}_{}_{}_{}_log.csv'\
        .format(alg, bw, delay, jitter, loss, attempt)