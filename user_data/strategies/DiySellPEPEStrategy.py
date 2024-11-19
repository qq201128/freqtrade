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

class DiySellPEPEStrategy(IStrategy):

    stoploss = -999

    INTERFACE_VERSION = 3

    position_adjustment_enable = True

    can_short = True

    timeframe = "5m"

    startup_candle_count: int = 200

    minPrice = 0.0

    

    # 例子特定变量
    max_entry_position_adjustment = 999
    # 该数字在下面有进一步说明
    max_dca_multiplier = 999



    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:


        dataframe["rsi"] = ta.RSI(dataframe) 

        return dataframe


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
      

        dataframe.loc[

            (

                (dataframe["rsi"] >99)

                &

                (dataframe['volume'] > 0)

            ),

            ['enter_long', 'long_tag']] = (1, 'enter_long_1') 

       

        #开空条件

        dataframe.loc[

            (

                (dataframe["rsi"] >10)

                &

                (dataframe['volume'] > 0)

            ),

            ['enter_short', 'short_tag']] = (1, 'enter_short') 

        return dataframe


    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        

        return dataframe
        


    #定义杠杆倍率

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
                 **kwargs) -> float:


        return 50.0
    

   


    
    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: Optional[float], max_stake: float,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> Optional[float]:
        # 获取当前的收盘价
        
        
        print("收盘价为："+str(current_rate)+"最大价格为："+str(self.minPrice))

        # 检查当前交易是否已经结束
        if trade.is_open is False:
            self.minPrice = 0.0

            return None

        # 初始化 maxPrice
        if self.minPrice == 0.0:
            self.minPrice = current_rate

        # 检查是否需要更新 maxPrice

        if self.minPrice - current_rate >= 0.000005:

            self.minPrice = current_rate

    
       # 计算当前持仓的爆仓价格
        leverage = self.leverage(trade.pair, current_time, current_rate, 1.0, 50.0, None, trade.side)
        liquidation_price = trade.liquidation_price(current_rate, leverage)

        # 计算距离爆仓价格的百分比
        distance_to_liquidation = (current_rate - liquidation_price) / current_rate

        # 如果距离爆仓价格还有 50%，则增加仓位使得距离变成 70%
        if distance_to_liquidation <= 0.50:
            # 计算目标距离爆仓价格的百分比
            target_distance_to_liquidation = 0.70

            # 计算目标爆仓价格
            target_liquidation_price = current_rate * (1 - target_distance_to_liquidation)

            # 计算需要增加的仓位数量
            current_position_size = trade.stake_amount
            target_position_size = current_position_size * (current_rate - liquidation_price) / (current_rate - target_liquidation_price)

            # 计算增加的仓位数量
            additional_stake = target_position_size - current_position_size

            # 确保增加的仓位数量不超过最大仓位限制
            additional_stake = min(additional_stake, max_stake)

            return additional_stake

    
            
        return None