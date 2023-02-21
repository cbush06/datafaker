class Sequence:
    _sequence: int = None
    _start: int = None
    _step: int = None

    def __init__(self, start = 0, step = 1):
        self._sequence = None
        self._start = start
        self._step = step
    
    def next(self):
        if(self._sequence == None):
            self._sequence = self._start - 1
        self._sequence += self._step
        return self._sequence