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
class DiyMaDing(IStrategy):

    stoploss = -999
    INTERFACE_VERSION = 3
    position_adjustment_enable = True
    timeframe = "15m"
    can_short = True
    startup_candle_count: int = 200

    def informative_pairs(self):

        # 获取白名单中的所有交易对。
        pairs = self.dp.current_whitelist()
        # 为每对交易对分配tf，以便可以为策略下载和缓存它们。
        informative_pairs = [(pair, '1d') for pair in pairs]
        # 可选的附加“静态”交易对
        informative_pairs += [
                              ("BTC/USDT:USDT", "15m"),
                            ]
        return informative_pairs

    @informative('1d')
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe) 
        return dataframe

    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe) 
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]

        # 添加金叉信号列
        dataframe["golden_cross"] =  (dataframe["macd"] > dataframe["macdsignal"]) 

        # 添加死叉信号列
        dataframe["death_cross"] =  (dataframe["macd"] < dataframe["macdsignal"]) 
        dataframe["ema_12"] = ta.EMA(dataframe,timeperiod=12)
        dataframe["ema_200"] = ta.EMA(dataframe,timeperiod=100)
        return dataframe


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if not self.dp:
            # 如果没有数据提供程序，则不执行任何操作。
            return dataframe

        dataframe['golden_cross_1h'] = dataframe['golden_cross_1h']
        dataframe['death_cross_1h'] = dataframe['death_cross_1h']
        dataframe["ema_12_1h"] = dataframe["ema_12_1h"]
        dataframe["ema_100_1h"] = dataframe["ema_100_1h"]
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]

        dataframe["ema_5m_12"] = ta.EMA(dataframe,timeperiod=12)
        dataframe["ema_5m_100"] = ta.EMA(dataframe,timeperiod=100)
        dataframe["rsi"] = ta.RSI(dataframe,timeperiod = 12)
       
        # 添加金叉信号列
        dataframe["golden_cross"] = (dataframe["macd"] > dataframe["macdsignal"]) & (dataframe["macd"].shift(1) <= dataframe["macdsignal"].shift(1))
        # 添加死叉信号列
        dataframe["death_cross"] = (dataframe["macd"] < dataframe["macdsignal"]) & (dataframe["macd"].shift(1) >= dataframe["macdsignal"].shift(1))


        return dataframe

    
    def total_price_cal(self,dataframe: DataFrame) -> DataFrame :
        # 获取信息交易对
        btc = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe="15m")
        btc_candle = btc.iloc[-1:]
        # 初始化总和
        total_sum = 0

        # 使用 for 循环遍历 btc_candle 的每一行
        for i in range(len(btc_candle)):
            # 计算每一条数据的 (close - open) / open
            change_percentage = (btc_candle['close'].iloc[i] - btc_candle['open'].iloc[i]) / btc_candle['open'].iloc[i] 
    
            # 将计算结果加到总和中
            total_sum += change_percentage
            
        dataframe["total_price"] = total_sum
        # print(total_sum)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        self.total_price_cal(dataframe)
        dataframe.loc[
            (
                (dataframe["golden_cross"])
                
                &
                (dataframe["ema_12_1h"] > dataframe["ema_100_1h"])
                &
                (dataframe['total_price']>0)
                &
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'long_tag']] = (1, 'enter_long_1') 
        
        dataframe.loc[
            (
                (dataframe["death_cross"])
               
                &
                (dataframe["ema_12_1h"] < dataframe["ema_100_1h"])
                &
                (dataframe['total_price']< 0 )
                &
                (dataframe['volume'] > 0)
            ),
            ['enter_short', 'short_tag']] = (1, 'enter_short_1') 

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
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
        
    
        #初始化投注金额
        if min_stake > proposed_stake:
            return min_stake
        else:
            return proposed_stake
    # 自定义退出信号
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
        
        if current_profit > 0.05:
                return "赚到钱了，跑"
        
       
        if trade.leverage< 50 :
             if current_profit>=0.005:
                  return "赚到钱了，跑"

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,

                              min_stake: Optional[float], max_stake: float,

                              current_entry_rate: float, current_exit_rate: float,

                              current_entry_profit: float, current_exit_profit: float,

                              **kwargs) -> Optional[float]:


        if trade.nr_of_successful_entries <=2 :
            if current_profit <=-1:
                return trade.nr_of_successful_entries
        if 2 < trade.nr_of_successful_entries <= 3:
            if current_profit <=-1:
                return trade.nr_of_successful_entries + 2
        if 3 < trade.nr_of_successful_entries <= 4:
            if current_profit <=-1:
                return trade.nr_of_successful_entries + 2
        if 4 < trade.nr_of_successful_entries <= 5:
            if current_profit <=-1:
                return trade.nr_of_successful_entries + 2
        if 5 < trade.nr_of_successful_entries <= 6:
            if current_profit <=-3:
                return (trade.nr_of_successful_entries + 2) * 1.5
        if 6 < trade.nr_of_successful_entries <= 7:
            if current_profit <=-3:
                return (trade.nr_of_successful_entries + 2)* 1.5
        if 7 < trade.nr_of_successful_entries <= 8:
            if current_profit <=-5:
                return (trade.nr_of_successful_entries + 2)* 2
        if 8 < trade.nr_of_successful_entries <= 9:
            if current_profit <=-5:
                return (trade.nr_of_successful_entries + 2)* 2
        if 9 < trade.nr_of_successful_entries <= 10:
            if current_profit <=-5:
                return (trade.nr_of_successful_entries + 2)* 2
        



        return None

    