from collections import namedtuple

Quality = namedtuple('Quality', ['bandwidth', 'delay', 'jitter', 'loss'])
Quality.__new__.__defaults__ = (None,) * len(Quality._fields)