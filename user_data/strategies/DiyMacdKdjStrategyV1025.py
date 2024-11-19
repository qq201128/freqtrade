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

class DiyMacdKdjStrategyV1025(IStrategy):
    stoploss = -0.25
    INTERFACE_VERSION = 3
    position_adjustment_enable = True
    can_short = True
    timeframe = "5m"
    startup_candle_count: int = 200
    minimal_roi = {
        "0": 0.2090,
        "39":0.078,
        "89":0.019
    }
    trailing_stop=  True
    trailing_stop_positive= 0.005
    trailing_stop_positive_offset=  0.108
    trailing_only_offset_is_reached=  True
   
   
    @informative('5m')
    @informative('30m')
    @informative('1h')
    @informative('4h')
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        #MACD线的9天简单移动平均。
        dataframe["macdsignal"] = macd["macdsignal"]
        #即MACD线与信号线的差值
        dataframe["macdhist"] = macd["macdhist"]
        
         # 计算KDJ指标 (使用默认参数)
        slowk, slowd = ta.STOCH(dataframe["high"], dataframe["low"], dataframe["close"],
                               fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        dataframe["k"] = slowk
        dataframe["d"] = slowd
        dataframe["j"] = 3 * dataframe["k"] - 2 * dataframe["d"]  # KDJ中的J线

        # 判断MACD是在0轴上方还是下方
        dataframe["macd_above_zero"] = dataframe["macd"] > 0

        # 判断MACD金叉和死叉
        dataframe["macd_golden_cross"] = (dataframe["macd"] > dataframe["macdsignal"])
        dataframe["macd_death_cross"] = (dataframe["macd"] < dataframe["macdsignal"]) 

        # 判断KDJ金叉和死叉
        dataframe["kdj_golden_cross"] = (dataframe["k"] > dataframe["d"])
        dataframe["kdj_death_cross"] = (dataframe["k"] < dataframe["d"])

        # 买入多（做多）条件
        dataframe["long"] = (dataframe["macd_golden_cross"] & dataframe["kdj_golden_cross"]) | \
                             (dataframe["macd_above_zero"] & dataframe["kdj_golden_cross"])

        # 买入空（做空）条件
        dataframe["short"] = (dataframe["macd_death_cross"] & dataframe["kdj_death_cross"]) | \
                             (~dataframe["macd_above_zero"] & dataframe["kdj_death_cross"])
    
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["long_5m"] ) &
                (dataframe["long_30m"]) &
                (dataframe["long_1h"]) &
                (dataframe["long_4h"])&
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'long_tag']] = (1, 'enter_long_1') 

        # 开空条件
        dataframe.loc[
            (
                (dataframe["short_5m"] ) &
                (dataframe["short_30m"]) &
                (dataframe["short_1h"]) &
                (dataframe["short_4h"])&
                (dataframe['volume'] > 0)
            ),
            ['enter_short', 'short_tag']] = (1, 'enter_short') 
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["short"])
            ),
            ['exit_long', 'exit_tag']] = (1, 'exit_long_1')
        
        dataframe.loc[
            (
                (dataframe["long"])
            ),
            ['exit_short', 'exit_tag']] = (1, 'exit_short_1')

        return dataframe

    # 定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
                 **kwargs) -> float:
        return 5.0

    