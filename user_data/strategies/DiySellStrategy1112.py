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
from freqtrade.exchange import timeframe_to_prev_date
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

class DiySellStrategy1112(IStrategy):
    stoploss = -999
    INTERFACE_VERSION = 3
    position_adjustment_enable = True
    can_short = True
    timeframe = "1m"
    startup_candle_count: int = 200
    
    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe) 
        return dataframe

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

       
        return proposed_stake

    # 自定义退出信号
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
       


        if current_profit > 0.05:
            # 平全部
            return "赚钱了跑"
    

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,

                              min_stake: Optional[float], max_stake: float,

                              current_entry_rate: float, current_exit_rate: float,

                              current_entry_profit: float, current_exit_profit: float,

                              **kwargs) -> Optional[float]:


         #获取K线数据
        dataframe = self.dp.ohlcv(trade.pair, timeframe="1h")
        # print(dataframe)
        candle = dataframe.iloc[-1].squeeze()
        #上一个k线的百分比
        last_proportion = (candle.close - candle.open) / candle.open * 100
        # 计算涨跌百分比
        #上一个K线的结束点位就是新K线的开盘价
        now_open = dataframe["close"] .iloc[-1]
        #获取最新价格就是最新的结束价格
        now_close = current_rate
        now_proportion = (now_close - now_open) / now_open * 100
        #计算2小时内波动
        result_proportion = now_proportion + last_proportion 

        # print(trade.nr_of_successful_entries)
        if trade.nr_of_successful_entries <=2 :
            if current_profit <= -0.01:
                print((trade.nr_of_successful_entries + 1) * 0.4)
                return (trade.nr_of_successful_entries + 1) * 0.4
        if trade.nr_of_successful_entries >2 and trade.nr_of_successful_entries <=3 :
                    if current_profit <= -0.01:
                        print(2.4)
                        return 2.4

        if trade.nr_of_successful_entries >3 and trade.nr_of_successful_entries <=4 :
                    if current_profit <= -0.01:
                        print(4.8 )
                        return 4.8 
        if trade.nr_of_successful_entries >4 and trade.nr_of_successful_entries <=5 :
                    if current_profit <= -0.01:
                        print(10 )
                        return 10.0
        if trade.nr_of_successful_entries >5 and trade.nr_of_successful_entries <=6 :
                    if current_profit <= -0.01:
                        print(20 )
                        return 20.0
        if trade.nr_of_successful_entries >6 and trade.nr_of_successful_entries <=7 :
                    if current_profit <= -0.01:
                        print(40)
                        return 40.0

    
        return None

    