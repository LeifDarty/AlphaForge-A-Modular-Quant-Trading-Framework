class IndicatorEngine:

    def __init__(self, data):
        self.data = data

    def add_mad_bands(self, window=15, k=2):

        self.data['median'] = self.data['close'].rolling(window).median()

        self.data['mad'] = (
                self.data['close'] - self.data['median']
        ).abs().rolling(window).median()

        self.data['upper'] = self.data['median'] + k * self.data['mad']
        self.data['lower'] = self.data['median'] - k * self.data['mad']

        return self.data

    def band_statistics(self):
        valid_data = self.data.dropna(subset=['close', 'upper', 'lower'])

        total = len(valid_data)

        below_lower = (valid_data['close'] < valid_data['lower']).sum()
        above_upper = (valid_data['close'] > valid_data['upper']).sum()

        return {
            "below_lower_%": (below_lower / total) * 100,
            "above_upper_%": (above_upper / total) * 100
        }

