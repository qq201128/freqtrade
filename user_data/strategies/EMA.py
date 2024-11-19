import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy as np
import talib.abstract as ta
from freqtrade.strategy import (IStrategy, informative,DecimalParameter)
from pandas import DataFrame, Series
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import math
import pandas_ta as pta
# from finta import TA as fta
import logging
from logging import FATAL
from functools import reduce
from datetime import datetime, timedelta
from freqtrade.persistence import Trade
from typing import Optional, Union

logger = logging.getLogger(__name__)

# NOT TO BE USED FOR LIVE!!!!!!

class multi_tf (IStrategy):

    def version(self) -> str:
        return "v1"

    INTERFACE_VERSION = 3


    can_short = True
    # ROI table:
    #超参数优化
    minimal_roi = {
        "360" : -1,
        "164": 0,
        "90": 0.015,
        #30分钟大于0.1平仓
        "60" : 0.03,
        "30": 0.1,
        "0": 0.2
    }

    # Stoploss:
    #止损
    stoploss = -0.1

    # Trailing stop:
    #当盈利到百分之5的时候 如果回退百分之1就平仓
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = True

    # Sell signal
    use_exit_signal = True
    exit_profit_only = False
    exit_profit_offset = 0.01
    ignore_roi_if_entry_signal = False

    timeframe = '5m'

    process_only_new_candles = True
    startup_candle_count = 100

    # This method is not required.
    # def informative_pairs(self): ...

     # Strategy parameters 阈值
    buy_umacd_max = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.01176, space="buy")
    buy_umacd_min = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.01416, space="buy")
    sell_umacd_max = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.00707, space="sell")
    sell_umacd_min = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.02323, space="sell")

    # Define informative upper timeframe for each pair. Decorators can be stacked on same
    # method. Available in populate_indicators as 'rsi_30m' and 'rsi_1h'.
    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema_120'] = ta.EMA(dataframe, timeperiod=120)
        return dataframe

    # 默认是5分钟的
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Strategy timeframe indicators for current pair.
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        # Informative pairs are available in this method.
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['rsi_6'] = ta.RSI(dataframe, timeperiod=6)
        # dataframe['umacd'] = (dataframe['ema_12'] / dataframe['ema_26']) - 1
        return dataframe

    #开仓条件
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       
       #开多条件
        dataframe.loc[
            (
                (dataframe["close"] > dataframe['ema_120_1h'])
                &
                # (dataframe['rsi_6']<20)
                # &
                #金叉 上一次ema12小于ema24 然后ema12大于ema24
                # qtpylib.crossed_above(dataframe['ema_12'],dataframe['ema_24'])
                # &
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'enter_tag']] = (1, 'long_1')
        
        #开空条件
        dataframe.loc[
            (
                (dataframe["close"] < dataframe['ema_120_1h'])
                &
                # (dataframe['rsi_6']>80)
                # &
                #金叉 上一次ema12小于ema24 然后ema12大于ema24
                # qtpylib.crossed_below(dataframe['ema_12'],dataframe['ema_24'])
                # &
                (dataframe['volume'] > 0)
            ),
            ['enter_short', 'enter_tag']] = (1, 'short_1')

        return dataframe
        # long_conditions = []
        # short_conditions = []
        # dataframe.loc[:, 'enter_tag'] = ''

        # # 做多 信号1 趋势类 ema金叉 
        # enter_long_1 = (
        #     (dataframe["close"] > dataframe['ema_120_1h'])
        #     &
        #     qtpylib.crossed_above(dataframe['ema_12'], dataframe['ema_26'])
        #     &
        #     (dataframe['volume'] > 0)
        # )
        # dataframe.loc[enter_long_1, 'enter_tag'] += 'enter_long_1_'
        # long_conditions.append(enter_long_1)

        # # 做多 信号2 抄底类 xxx
        # enter_long_2 = (
        #     (dataframe['umacd'].between(self.buy_umacd_min.value, self.buy_umacd_max.value))
        #     &
        #     (dataframe['volume'] > 0)
        # )
        # dataframe.loc[enter_long_2, 'enter_tag'] += 'enter_long_2_'
        # long_conditions.append(enter_long_2)

        # if long_conditions:
        #     dataframe.loc[
        #         reduce(lambda x, y: x | y, long_conditions),
        #         'enter_long'
        #     ]=1
        # else:
        #     dataframe.loc[(), ['enter_long', 'enter_tag']] = (0, 'no_long_entry')

    #平仓
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                (dataframe["rsi_6"] <= 80)
                &
                (dataframe['volume'] > 0)
            ),
            ['exit_long', 'exit_tag']] = (1, 'exit_long_1')
        
        dataframe.loc[
            (
                (dataframe["rsi_6"] > 20)
                &
                (dataframe['volume'] > 0)
            ),
            ['exit_short', 'exit_tag']] = (1, 'exit_short_1')

        return dataframe
    #     dataframe.loc[(), ['exit_long', 'exit_tag']] = (0, 'no_long_exit')
    #     dataframe.loc[(), ['exit_short', 'exit_tag']] = (0, 'no_short_exit')
    # def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
    #                         time_in_force: str, current_time: datetime, entry_tag: Optional[str], 
    #                         side: str, **kwargs) -> bool:

    #     # if entry_tag == "":
    #     #     return False

    #     return True

    # def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float,
    #                 current_profit: float, **kwargs):

    #     # current_time ++
    #     # candle 指标
    #     dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    #     last_candle = dataframe.iloc[-1].squeeze()

    #     if trade.enter_tag == 'enter_long_1_':
    #         if last_candle['close'] < last_candle['ema_120_1h']:
    #             return "custom_exit_long_1"

    # def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str, amount: float,
    #                        rate: float, time_in_force: str, exit_reason: str,
    #                        current_time: datetime, **kwargs) -> bool:

    #     # # umacd 信号 不想使用 exit_signal
    #     # if trade.enter_tag == "enter_long_2_" and exit_reason == "exit_signal":
    #     #     return False
    
    #     return True
