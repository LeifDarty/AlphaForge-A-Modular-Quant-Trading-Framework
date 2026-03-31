class RiskManager:

    def __init__(self, per_trade_risk, max_daily_loss):

        self.per_trade_risk = per_trade_risk
        self.max_daily_loss = max_daily_loss

        self.daily_loss = 0
        self.trading_allowed = True

    def reset_day(self):
        self.daily_loss = 0
        self.trading_allowed = True

    def can_take_trade(self):
        return self.trading_allowed

    def update_pnl(self, pnl):
        #  loss track
        if pnl < 0:
            self.daily_loss += abs(pnl)

        # check daily limit hit
        if self.daily_loss >= self.max_daily_loss:
            self.trading_allowed = False

    def get_position_size(self, entry, stoploss, lot_size):

        # risk-based position sizing

        risk_per_unit = abs(entry - stoploss)

        if risk_per_unit == 0:
            return 0

        qty = self.per_trade_risk / risk_per_unit

        # round to nearest lot
        qty = int(qty // lot_size) * lot_size

        return max(qty, 0)