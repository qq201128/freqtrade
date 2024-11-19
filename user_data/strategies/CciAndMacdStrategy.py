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
class CciAndMacdStrategy(IStrategy):
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short=True

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        # "120": 0.0,  # exit after 120 minutes at break even
        "0": 0.4,
        "35": 0.249,
        "81": 0.16,
        "120": 0.03,
        "150":-1
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.5

    position_adjustment_enable = True

    # Trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.25
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = "15m"

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the config.
    use_exit_signal = False
    exit_profit_only = False
    exit_profit_offset = 0.03
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 200

    # Optional order type mapping.
    # order_types = {
    #     "entry": "limit",
    #     "exit": "limit",
    #     "stoploss": "market",
    #     "stoploss_on_exchange": False,
    # }

    # Optional order time in force.
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    @property
    def protections(self):
        return  [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 5
            }
        ]
    plot_config = {
        # "main_plot": {
        #     "cci": {},
        # },
        "subplots": {
            "MACD": {
                "macd": {"color": ""},
                "macdsignal": {"color": ""},
            },
            "cci": {
                "cci": {"color": ""},
                "macd_golden_cross": {"color": ""},
                "macd_death_cross": {"color": ""},
            }
        },
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       

        # # Commodity Channel Index: values [Oversold:-100, Overbought:100]
        #超买/超卖信号：CCI值超过+100或低于-100可以作为超买或超卖的信号。
        #趋势识别：CCI值持续在+100以上或-100以下可能表明趋势的强度。
        dataframe['cci'] = ta.CCI(dataframe)

        

        # Stochastic Fast
        #使用快速Stochastic来捕捉市场的短期波动，并尝试在趋势的早期阶段进入交易。然而，由于快速Stochastic较为敏感，它可能会产生误导性的信号
        stoch_fast = ta.STOCHF(dataframe)
        dataframe["fastd"] = stoch_fast["fastd"]
        dataframe["fastk"] = stoch_fast["fastk"]


        # MACD
        #通过计算两个不同周期的指数移动平均线（EMA）之间的差异来反映价格的动态。
        #MACD是一个滞后指标，它反映了历史价格信息，因此可能会有延迟
        #当macd线下穿madcsignal的时候 买跌 当上穿的时候买涨 
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        #MACD线的9天简单移动平均。
        dataframe["macdsignal"] = macd["macdsignal"]
        #即MACD线与信号线的差值
        dataframe["macdhist"] = macd["macdhist"]
        # 判断金叉
        dataframe['macd_golden_cross'] = qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])

        # 判断死叉
        dataframe['macd_death_cross'] = qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal'])


        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        long_conditions = []
        short_conditions = []

        entry_long_1 = (
                #cci大于100
                (dataframe["cci"] > 100)
                &
                #macd金叉
                qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])
                &
                (dataframe["volume"] > 0)
        )
        long_conditions.append(entry_long_1)
        
        entry_long_2 = (
            (dataframe['macd'] > dataframe['macdsignal'])
            & (dataframe['macd'].shift(1) <= dataframe['macdsignal'].shift(1))
            & (dataframe["volume"] > 0)
        )
        long_conditions.append(entry_long_2)

        if long_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, long_conditions), 'enter_long'] = 1

        entry_short_1 = (
            ##cci小于-100
            (dataframe["cci"] < -100)
            &
            #macd死叉
            qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal'])
            &
            (dataframe["volume"] > 0)
        )
        short_conditions.append(entry_short_1)

        entry_short_2 = (
            (dataframe['macd'] < dataframe['macdsignal'])
            & (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1))
            & (dataframe["volume"] > 0)
        )
        short_conditions.append(entry_short_2)
       
        if short_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, short_conditions), 'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        exit_long_conditions = []
        exit_short_conditions = []

        # Long exit conditions
        exit_long_1 = (
            (dataframe["cci"] < 100) &
            (dataframe["cci"] > 50) &
            (dataframe["volume"] > 0)  # Ensure volume is not 0
        )
        exit_long_conditions.append(exit_long_1)

        exit_long_2 = (
            qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']) &
            (dataframe["volume"] > 0)  # Ensure volume is not 0
        )
        exit_long_conditions.append(exit_long_2)

        if exit_long_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, exit_long_conditions), 'exit_long'] = 1

        # Short exit conditions
        exit_short_1 = (
            (dataframe["cci"] > -100) &
            (dataframe["cci"] < 50) &
            (dataframe["volume"] > 0)  # Ensure volume is not 0
        )
        exit_short_conditions.append(exit_short_1)

        exit_short_2 = (
            qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']) &
            (dataframe["volume"] > 0)  # Ensure volume is not 0
        )
        exit_short_conditions.append(exit_short_2)

        if exit_short_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, exit_short_conditions), 'exit_short'] = 1

        return dataframe
    #定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float, proposed_leverage: float, max_leverage: float, entry_tag:str, side: str, **kwargs) -> float:

        return 50.0
    
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:

        # 我们需要留下大部分资金用于可能的进一步 DCA 订单
        # 这同样适用于固定投注
        Trade.n
        return 20

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: Optional[float], max_stake: float,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> Optional[float]:
        """
        自定义交易调整逻辑，返回应增加或减少的下注金额。
        这意味着额外的入场或退出订单，带有额外的费用。
        仅当`position_adjustment_enable`设置为True时才会调用。

        有关完整文档，请访问 https://www.freqtrade.io/zh/latest/strategy-advanced/

        当策略未实现时，返回 None

        :param trade: 交易对象。
        :param current_time: 包含当前日期和时间的日期时间对象
        :param current_rate: 当前入场报价（与 current_entry_profit 相同）
        :param current_profit: 当前利润（作为比例），基于 current_rate 计算（与 current_entry_profit 相同）。
        :param min_stake: 交易所允许的最小投注额（适用于入场和退出）
        :param max_stake: 允许的最大投注额（通过余额或交易所限制）
        :param current_entry_rate: 使用入场定价的当前汇率。
        :param current_exit_rate: 使用退出定价的当前汇率。
        :param current_entry_profit: 使用入场定价的当前利润。
        :param current_exit_profit: 使用退出定价的当前利润。
        :param **kwargs: 请确保将其保留在此处，以免破坏您的策略。
        :return float: 调整交易的下注金额，
                       正值为增加仓位，负值为减少仓位。
                       返回 None 表示不采取任何操作。
        """

        if current_profit > 0.05 and trade.nr_of_successful_exits == 0:
            # 当利润达到 +5% 时，取利润的一半
            return -(trade.stake_amount / 2)

        if current_profit > -0.05:
            return None

        # 获取双向数据框（仅用于展示访问方法）
        dataframe, _ = self.dp.get_analyzed_dataframe(trade.pair, self.timeframe)
        # 当价格不活跃下跌时才购买。
        last_candle = dataframe.iloc[-1].squeeze()
        previous_candle = dataframe.iloc[-2].squeeze()
        if last_candle['close'] < previous_candle['close']:
            return None

        count_of_entries = trade.nr_of_successful_entries
        if count_of_entries < 2:
            return 20

        return None