class Config:
    def __init__(self, data_dict: dict):
        self._algs = data_dict['algorithms']
        self._bws = data_dict['bandwidths']
        self._delays = data_dict['delays']
        self._jitters = data_dict['jitters']
        self._losses = data_dict['losses']
        self._num_attempts = data_dict['num_attempts']
        self._time = data_dict.get('time', 60)

    @property
    def algorithms(self):
        return self._algs

    @property
    def bandwidths(self):
        return self._bws

    @property
    def delays(self):
        return self._delays

    @property
    def jitters(self):
        return self._jitters

    @property
    def losses(self):
        return self._losses

    @property
    def num_attempts(self):
        return self._num_attempts

    @property
    def time(self):
        return self._time
