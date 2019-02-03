import os
import pytest
from src.utils import *

dirname = os.path.dirname(os.path.abspath(__file__))

def test_init_quality():
    q = Quality(1, 2, 3, 4)
    assert q.bandwidth == 1
    assert q.delay == 2
    assert q.jitter == 3
    assert q.loss == 4

def test_quality_to_tc():
    q = Quality(1, 2, 3, 4)
    tc_q = q.to_tc_quality()    
    assert tc_q.bandwidth == 1 / 8
    assert tc_q.delay == 2
    assert tc_q.jitter == 3 * 2 / 100
    assert tc_q.loss == 4

def test_quality_from_tc():
    q = Quality(1, 2, 3, 4)
    tc_q = q.to_tc_quality()
    q2 = Quality.from_tc_quality(tc_q)
    assert q == q2

def test_quality_to_tuple():
    q = Quality(1, 2, 3, 4)
    assert q.to_tuple() == (1, 2, 3, 4)

def test_parse_srv_out():
    speed = parse_server_out(
        os.path.join(dirname, 'test_data/srv_out.json')
    )
    assert speed == 961361.430820

def test_parse_view():
    res = parse_view(
        os.path.join(dirname, 'test_data/view_out.txt')
    )
    assert res == (0, 58995)

def test_parse_res():
    res = parse_res(
        os.path.join(dirname, 'test_data/res_out.csv')
    )
    assert len(res) > 0
    assert res[Quality(1, 1, 0, 0.0001)] == 'reno'

def test_parse_res_per_alg():
    res = parse_res_per_alg(
        os.path.join(dirname, 'test_data/res_per_alg_out.csv')
    )
    assert len(res) > 0
    assert res[Quality(1, 1, 0, 0.0001)] - 953836.6202723333 < 0.00001

@pytest.mark.parametrize('alg,quality,attempt,expected', [
        ('bbr', Quality(1, 1, 20, 0.001), 0, 'net_bbr_0.125_1_0.2_0.001_0_server.json'),
        ('bbr', Quality(1, 1, 20, 1.0), 1, 'net_bbr_0.125_1_0.2_1_1_server.json'),
        ('cubic', Quality(1, 1, 0, 0.001), 2, 'net_cubic_0.125_1_0.0_0.001_2_server.json'),
    ])
def test_srv_out_name(alg, quality, attempt, expected):
    name = get_srv_out_name(alg, quality, attempt)
    assert name == expected

