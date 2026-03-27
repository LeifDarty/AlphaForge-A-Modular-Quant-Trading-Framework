import pandas as pd

class DataHandler:

    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)

        self.data['datetime'] = pd.to_datetime(self.data['datetime'])
        self.data.set_index('datetime', inplace=True)

        self.data.sort_index(inplace=True)

    def get_data(self):
        return self.data