# Import necessary libraries
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from datetime import datetime, timedelta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class DoubleBottomTopHunterStrategyV1(IStrategy):
    # Define the minimal ROI (Return on Investment)
    minimal_roi = {
        "0": 0.28300000000000003,
        "25": 0.096,
        "80": 0.039,
        "183": 0
    }

    # Define the stoploss
    stoploss = -0.327

    # Define the timeframe
    timeframe = '1m'

    # Define the startup candle count
    startup_candle_count = 200
    INTERFACE_VERSION = 3
    can_short=True
    trailing_stop= True
    trailing_stop_positive= 0.011
    trailing_stop_positive_offset=0.032
    trailing_only_offset_is_reached= True

    @property
    def protections(self):
        return  [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 3
            }
        ]

    plot_config = {
        "main_plot": {
            "sma_short": {},
            "sma_mid": {},
            "sma_long": {},
            "sma_very_long": {},
        },
        "subplots": {
            "Volume": {
                "avg_volume": {"color": ""}
            }
        },
    }
    period_length =100
    lookback_period =100

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe['low1'] = ta.MIN(dataframe['low'], self.period_length)
        dataframe['high1'] = ta.MAX(dataframe['high'], self.period_length)

        dataframe['low2'] = dataframe['low'].shift(1)
        dataframe['high2'] = dataframe['high'].shift(1)

        dataframe['double_bottom'] = (
            (dataframe['low'] == dataframe['low1']) &
            (dataframe['low'] == dataframe['low2']) &
            (ta.MIN(dataframe['low'], self.lookback_period) == dataframe['low1'])
        )

        dataframe['double_top'] = (
            (dataframe['high'] == dataframe['high1']) &
            (dataframe['high'] == dataframe['high2']) &
            (ta.MAX(dataframe['high'], self.lookback_period) == dataframe['high1'])
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Long condition
        dataframe.loc[
            (
                (dataframe['double_bottom'])&
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        # Short condition
        dataframe.loc[
            (
                (dataframe['double_top'])&
                (dataframe['volume'] > 0)
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Sell condition for long positions
        dataframe.loc[
            (
                (dataframe['double_bottom'])&
                (dataframe['volume'] > 0)
            ),
            'exit_short'] = 1

        # Sell condition for short positions
        dataframe.loc[
            (
                (dataframe['double_top'])&
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
     #定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float, proposed_leverage: float, max_leverage: float, entry_tag:str, side: str, **kwargs) -> float:

        return 50.0