from backtesting import Strategy, Backtest
from config import SL_PERCENTAGE, TP_PERCENTAGE, POSITION_SIZE

class PatternStrategy(Strategy):
    sl_perc = SL_PERCENTAGE
    tp_perc = TP_PERCENTAGE
    mysize = POSITION_SIZE
    
    def init(self):
        super().init()
        # get signal column from the data
        self.signal = self.I(lambda: self.data.TotalSignal)
    
    def next(self):
        super().next()
        
        # if buy signal and no current position
        if self.signal[-1] == 2 and not self.position:
            # new long position with calculated sl and tp
            current_close = self.data.Close[-1]
            sl = current_close - self.sl_perc * current_close  # sl at x% below the close price
            tp = current_close + self.tp_perc * current_close  # tp at y% above the close price
            self.buy(size=self.mysize, sl=sl, tp=tp)
        
        # if sell signal and no current position
        elif self.signal[-1] == 1 and not self.position:
            # new short position with calculated sl and tp
            current_close = self.data.Close[-1]
            sl = current_close + self.sl_perc * current_close  # sl at x% above the close price
            tp = current_close - self.tp_perc * current_close  # tp at y% below the close price
            self.sell(size=self.mysize, sl=sl, tp=tp)

def run_backtest(dataframes):
    results = []
    heatmaps = []
    
    for df in dataframes:
        bt = Backtest(df, PatternStrategy, cash=5000, margin=1/5, commission=0.0002)
        stats, heatmap = bt.optimize(
            sl_perc=[i/100 for i in range(1, 8)],
            tp_perc=[i/100 for i in range(1, 8)],
            maximize='Return [%]', 
            max_tries=3000,
            random_state=0,
            return_heatmap=True
        )
        results.append(stats)
        heatmaps.append(heatmap)
    
    return results, heatmaps
