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
    IntParameter,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class DiyBuyStrategy1109(IStrategy):

    stoploss = -999
    INTERFACE_VERSION = 3
    position_adjustment_enable = True
    can_short = True
    timeframe = "1m"
    startup_candle_count: int = 200
    #补仓次数
    useNumber = 0


    @property
    def protections(self):
        return  [
            
            {
                #如果在最近的24个蜡烛内的一个交易利润小于百分之200 锁定1000分钟
                "method": "LowProfitPairs",
                "lookback_period_candles": 1,
                "trade_limit": 1,
                "stop_duration": 1000,
                "required_profit": -2
            }
        ]
    
    @informative('15m')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe) 
        return dataframe


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe["rsi"] = ta.RSI(dataframe) 

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
      
        dataframe.loc[
            (
                (dataframe["rsi"] >10)
                &
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'long_tag']] = (1, 'enter_long_1') 

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[:, ['exit_long', 'exit_tag']] = (0, 'long_out')
        return dataframe

    #定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
                 **kwargs) -> float:

        return 50.0
    
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                        proposed_stake: float, min_stake: Optional[float], max_stake: float,
                        leverage: float, entry_tag: Optional[str], side: str,
                        **kwargs) -> float:

       
        #重置补仓次数
        self.useNumber = 0
        return proposed_stake

    # 自定义退出信号
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
       

        #获取K线数据
        dataframe = self.dp.ohlcv(trade.pair, timeframe="15m")
        candle = dataframe.iloc[-1].squeeze()
        #上一个k线的百分比
        last_proportion = (candle.close - candle.open) / candle.open * 100
        # 计算涨跌百分比
        #上一个K线的结束点位就是新K线的开盘价
        now_open = dataframe["close"] .iloc[-1]
        #获取最新价格就是最新的结束价格
        now_close = current_rate
        now_proportion = (now_close - now_open) / now_open * 100
        #如果30分钟之内上升百分比超过了百分之10 清仓
        result_proportion = now_proportion + last_proportion 
        if result_proportion > 10 :
            # 平全部
            return "瀑布了，清仓跑路"

        if self.useNumber == 3 :
            if current_profit <= -1.3:
                return "补仓次数为3且亏损130%"


        if self.useNumber == 0:
            if current_profit > 0.3:
                    # 平全部
                    return "赚了30%"

        if self.useNumber ==1 :
            if current_profit > 0.25:
                # 平全部
                return "补仓次数为1且赚了25%"
            
        if self.useNumber >=2 :
            if current_profit > 0.1:
                # 平全部
                return "补仓次数为2且赚了10%"
    

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,

                              min_stake: Optional[float], max_stake: float,

                              current_entry_rate: float, current_exit_rate: float,

                              current_entry_profit: float, current_exit_profit: float,

                              **kwargs) -> Optional[float]:

        # 补仓金额列表
        add_stake_amounts = [6, 18, 54]

    
        if self.useNumber == 0 :
             if current_profit <= -1:
                self.useNumber = self.useNumber + 1
                # 根据补仓次数返回不同的补仓金额
                return add_stake_amounts[self.useNumber - 1]

        if self.useNumber == 1 :
             if current_profit <= -1.5:
                self.useNumber = self.useNumber + 1
                # 根据补仓次数返回不同的补仓金额
                return add_stake_amounts[self.useNumber - 1]

        if self.useNumber == 2 :
             if current_profit <= -2:
                self.useNumber = self.useNumber + 1
                # 根据补仓次数返回不同的补仓金额
                if self.useNumber <= len(add_stake_amounts):
                    return add_stake_amounts[self.useNumber - 1]
                
        
    
        return None

    