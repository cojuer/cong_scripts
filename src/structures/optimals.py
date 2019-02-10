import os

from src.structures.quality import Quality

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict


class Optimals:
    def __init__(self, fp):
        self._speed: 'Dict[Quality, float]' = {}
        self._algs: 'Dict[Quality, str]' = {}
        for line in fp:
            if len(line) == 0:
                break
            bandwidth, delay, jitter, loss, speed, algorithm = \
                [word.strip() for word in line.split(',')]
            tmp = Quality(
                bandwidth=float(bandwidth),
                delay=float(delay),
                jitter=float(jitter),
                loss=float(loss)
            )
            self._speed[tmp] = float(speed)
            self._algs[tmp] = algorithm

    def get_optimal_alg(self, quality: 'Quality') -> str:
        return self._algs[quality]

    def get_optimal_speed(self, quality: 'Quality') -> float:
        return self._speed[quality]


if __name__ == '__main__':
    with open('data/test/optimals.txt', 'w') as file:
        file.write('1, 2, 3, 4, 5, test_alg')
    try:
        with open('data/test/optimals.txt', 'r') as file:
            optimals = Optimals(file)
        test_quality = Quality(bandwidth=1, delay=2, jitter=3, loss=4)
        assert optimals.get_optimal_speed(test_quality) == 5
        assert optimals.get_optimal_alg(test_quality) == 'test_alg'
    except Exception as e:
        raise
    finally:
        os.remove('data/test/optimals.txt')
