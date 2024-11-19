# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# flake8: noqa: F401

# isort: skip_file

# --- Do not remove these libs ---

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

    DecimalParameter,

    IStrategy,

    IntParameter,

)


# --------------------------------

# Add your lib to import here

import talib.abstract as ta

import freqtrade.vendor.qtpylib.indicators as qtpylib



# This class is a sample. Feel free to customize it.

class DiySellStrategy(IStrategy):
    stoploss = -999
    INTERFACE_VERSION = 3
    position_adjustment_enable = True
    can_short = True
    timeframe = "5m"
    startup_candle_count: int = 200
    
    # 使用字典来存储每个币种的 maxPrice
    maxPrice = 0.0
    
    nowUsdt = 0.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe) 
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > 99) &
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'long_tag']] = (1, 'enter_long_1') 

        # 开空条件
        dataframe.loc[
            (
                (dataframe["rsi"] > 10) &
                (dataframe['volume'] > 0)
            ),
            ['enter_short', 'short_tag']] = (1, 'enter_short') 
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    # 定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
                 **kwargs) -> float:
        return 50.0

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:
         # 检查当前交易是否已经结束
        for trade in Trade.get_trades([Trade.pair == pair, Trade.is_open.is_(False)]):
            self.maxPrice = 0.0
            print("交易已关闭，重置 maxPrice 为 0.0")

        return proposed_stake

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: Optional[float], max_stake: float,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> Optional[float]:

        # 初始化 maxPrice
        if self.maxPrice == 0.0:
            self.maxPrice = current_rate
            self.nowUsdt = trade.stake_amount

        # 检查是否需要更新 maxPrice
        if current_rate >= self.maxPrice + 0.00055:
            self.maxPrice = current_rate
            self.nowUsdt = self.nowUsdt + 0.1
            return self.nowUsdt
            
        if current_profit > 0.5 and trade.nr_of_successful_exits == 0:
            # 当利润达到 百分之50 时，取利润的一半
            return -(trade.stake_amount / 2)
            

        return None