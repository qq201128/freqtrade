# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from freqtrade.constants import ListPairsWithTimeframes
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from datetime import datetime, timedelta
from typing import Optional, Union
from freqtrade.persistence import Order, PairLocks, Trade
from functools import reduce
from freqtrade.strategy import (IStrategy, informative,DecimalParameter)
from freqtrade.strategy import (
    BooleanParameter,
    CategoricalParameter,
    IntParameter,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class TwoWayStrategy(IStrategy):

    stoploss = -999
    INTERFACE_VERSION = 3
    position_adjustment_enable = True
    timeframe = "5m"
    can_short = True
    startup_candle_count: int = 200


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe["rsi"] = ta.RSI(dataframe) 
        

        return dataframe

    
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe.loc[
            (
            
                (dataframe["rsi"] > 50)
                &
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'long_tag']] = (1, 'enter_long_1') 
        
        # dataframe.loc[
        #     (
                
        #         (dataframe["rsi"] < 50)
        #         &
        #         (dataframe['volume'] > 0)
        #     ),
        #     ['enter_short', 'short_tag']] = (1, 'enter_short_1') 

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        return dataframe

    #定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
                 **kwargs) -> float:

        return 50.0
    
   

    