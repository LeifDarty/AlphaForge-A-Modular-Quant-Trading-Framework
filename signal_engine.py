import numpy as np

class SignalEngine:

    def __init__(self, data):
        self.data = data

    def generate_signals(self):

        self.data['signal'] = np.select(
            [
                (self.data['open'].shift(1) > self.data['lower']) &
                (self.data['low'] < self.data['lower']),

                (self.data['open'].shift(1) < self.data['upper']) &
                (self.data['high'] > self.data['upper'])
            ],
            [1, -1],
            default=0
        )

        return self.data
