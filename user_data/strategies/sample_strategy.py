# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from datetime import datetime, timedelta
from typing import Optional, Union
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
class SampleStrategy1(IStrategy):
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
        "60":0.1,
        "30": 0.25,
        "0": 0.5,
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.5

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.5
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = "1h"

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    exit_profit_offset = 0.03
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    buy_rsi = IntParameter(low=1, high=50, default=30, space="buy", optimize=True, load=True)
    sell_rsi = IntParameter(low=50, high=100, default=70, space="sell", optimize=True, load=True)
    short_rsi = IntParameter(low=51, high=100, default=70, space="sell", optimize=True, load=True)
    exit_short_rsi = IntParameter(low=1, high=50, default=30, space="buy", optimize=True, load=True)


    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 200

    # Optional order type mapping.
    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    # Optional order time in force.
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    plot_config = {
        "main_plot": {
            "tema": {},
            "sar": {"color": ""},
        },
        "subplots": {
            "MACD": {
                "macd": {"color": ""},
                "macdsignal": {"color": ""},
            },
            "RSI": {
                "rsi": {"color": ""},
            },
            "Bollinger": {
                "wbb_middleband": {"color": ""},
            },
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
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # Momentum Indicators
        # ------------------------------------

        # ADX
        dataframe["adx"] = ta.ADX(dataframe)

        #+DI 指标衡量的是上升动量的强度。它是通过比较当前周期的最高价与前一周期的最高价来计算的。如果当前周期的最高价高于前一周期的最高价，那么上升动量被认为是正的。
        #-DI 指标衡量的是下降动量的强度。它是通过比较当前周期的最低价与前一周期的最低价来计算的。如果当前周期的最低价低于前一周期的最低价，那么下降动量被认为是负的。
        #当 +DI 线高于 -DI 线时，可能表明上升趋势。
        #当 -DI 线高于 +DI 线时，可能表明下降趋势。
        # # Plus Directional Indicator / Movement
        # dataframe['plus_dm'] = ta.PLUS_DM(dataframe)
        # dataframe['plus_di'] = ta.PLUS_DI(dataframe)

        # # Minus Directional Indicator / Movement
        # dataframe['minus_dm'] = ta.MINUS_DM(dataframe)
        # dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        #Aroon指标显示了从当前日期起，价格达到新高或新低以来的周期数。
        #确定趋势的强度：如果Aroon Up或Aroon Down的值接近100，表明趋势很强。
        #识别趋势的转变：当Aroon Oscillator从负值变为正值时，可能是上升趋势的开始；反之，可能是下降趋势的开始。
        #作为交易信号：Aroon Oscillator的交叉可以作为买入或卖出的信号。
        # # Aroon, Aroon Oscillator
        # aroon = ta.AROON(dataframe)
        # dataframe['aroonup'] = aroon['aroonup']
        # dataframe['aroondown'] = aroon['aroondown']
        # dataframe['aroonosc'] = ta.AROONOSC(dataframe)

        #Awesome Oscillator是一个无方向的指标，它不预测市场的方向，而是衡量动能的变化。
        # # Awesome Oscillator
        # dataframe['ao'] = qtpylib.awesome_oscillator(dataframe)

        # # Keltner Channel
        #中间线（Middle Line）：通常是10日简单移动平均线（SMA），代表价格的平均水平，作为通道的中心。
        #上轨线（Upper Channel Line）：中间线加上一定倍数的标准差，通常使用2倍标准差。这表示价格波动的上限。
        #下轨线（Lower Channel Line）：中间线减去一定倍数的标准差，同样通常使用2倍标准差。这表示价格波动的下限。
        #趋势识别：如果价格保持在中间线之上，可能表明上升趋势；如果价格保持在中间线之下，可能表明下降趋势。
        #支撑和阻力：上轨线和下轨线可以作为潜在的阻力和支撑水平。价格接近这些线时可能会遇到买卖压力。
        #交易信号：价格突破上轨线可能表明超买情况，是潜在的卖出信号；价格跌破下轨线可能表明超卖情况，是潜在的买入信号。
        # keltner = qtpylib.keltner_channel(dataframe)
        # dataframe["kc_upperband"] = keltner["upper"]
        # dataframe["kc_lowerband"] = keltner["lower"]
        # dataframe["kc_middleband"] = keltner["mid"]
        # dataframe["kc_percent"] = (
        #     (dataframe["close"] - dataframe["kc_lowerband"]) /
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"])
        # )
        # dataframe["kc_width"] = (
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"]) / dataframe["kc_middleband"]
        # )

        # # Ultimate Oscillator
        #终极振荡器的值范围从0到100。值接近0可能表示超卖条件，而值接近100可能表示超买条件。
        #趋势强度：较高的UO值通常表明上升趋势的强度，而较低的UO值可能表明下降趋势的强度。
        # dataframe['uo'] = ta.ULTOSC(dataframe)

        # # Commodity Channel Index: values [Oversold:-100, Overbought:100]
        #超买/超卖信号：CCI值超过+100或低于-100可以作为超买或超卖的信号。
        #趋势识别：CCI值持续在+100以上或-100以下可能表明趋势的强度。
        # dataframe['cci'] = ta.CCI(dataframe)

        # RSI
        dataframe["rsi"] = ta.RSI(dataframe)

        # # Inverse Fisher transform on RSI: values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        #当RSI为50时，逆Fisher变换的结果是0，表示中性或平衡状态。当RSI接近100时，逆Fisher变换的结果接近1.0，表示极端超买状态；当RSI接近0时，结果接近-1.0，表示极端超卖状态。
        # rsi = 0.1 * (dataframe['rsi'] - 50)
        # dataframe['fisher_rsi'] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

        # # Inverse Fisher transform on RSI normalized: values [0.0, 100.0] (https://goo.gl/2JGGoy)
        # dataframe['fisher_rsi_norma'] = 50 * (dataframe['fisher_rsi'] + 1)

        # # Stochastic Slow
        #Stochastic Oscillator的计算基于过去一定时期内的收盘价与该时期内价格范围的比较。
        #%K是Stochastic Oscillator的快速线，N是选定的周期长度，通常是14天。
        #%K的移动平均值来创建一个更平滑的指标，称为%D线：
        #%K线和%D线。当%K线从下方穿越%D线时，这可能被视为买入信号；当%K线从上方穿越%D线时，则可能被视为卖出信号。
        # 此外，如果Stochastic Slow的值接近0，则可能表明市场处于超卖状态，而接近100则可能表明市场处于超买状态。
        # stoch = ta.STOCH(dataframe)
        # dataframe['slowd'] = stoch['slowd']
        # dataframe['slowk'] = stoch['slowk']

        # Stochastic Fast
        #使用快速Stochastic来捕捉市场的短期波动，并尝试在趋势的早期阶段进入交易。然而，由于快速Stochastic较为敏感，它可能会产生误导性的信号
        stoch_fast = ta.STOCHF(dataframe)
        dataframe["fastd"] = stoch_fast["fastd"]
        dataframe["fastk"] = stoch_fast["fastk"]

        # # Stochastic RSI
        #通过将随机震荡指标公式应用于相对强弱指数（RSI）值，而不是直接应用于价格数据，来提供对超买或超卖情况的更敏感的视角
        #StochRSI的读数超过0.8时，通常被视为超买信号，而低于0.2则被视为超卖信号
        # Please read https://github.com/freqtrade/freqtrade/issues/2961 before using this.
        # STOCHRSI is NOT aligned with tradingview, which may result in non-expected results.
        # stoch_rsi = ta.STOCHRSI(dataframe)
        # dataframe['fastd_rsi'] = stoch_rsi['fastd']
        # dataframe['fastk_rsi'] = stoch_rsi['fastk']

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

        # MFI
        #衡量买卖压力和交易量之间的关系
        #超买/超卖：MFI通常在0到100之间波动。当MFI高于80时，市场可能被认为是超买的，表明买方压力可能过度，价格可能会下跌。当MFI低于20时，市场可能被认为是超卖的，表明卖方压力可能过度，价格可能会上涨。
        #趋势确认：MFI可以用来确认价格趋势的强度。如果价格上涨，MFI也应该上升，这表明上涨趋势是健康的。
        #交叉信号：MFI的短期移动平均线（如5天或10天）可以用来生成交易信号。当短期MFI线从下向上穿过长期MFI线时，可能是一个买入信号；反之，则可能是一个卖出信号
        dataframe["mfi5"] = ta.MFI(dataframe,timedelta = 5)
        dataframe["mfi10"] = ta.MFI(dataframe,timedelta = 10)

        # # ROC
        #衡量某一特定资产价格相对于之前某个时间点的变化率
        #动量变化：ROC可以反映价格的动量变化。一个上升的ROC值表明价格上涨的速率在加快，而一个下降的ROC值表明价格下跌的速率在加快。
        #超买/超卖：ROC也可以用于识别超买或超卖条件。如果ROC值非常高，可能表明市场过热，价格可能会回调。相反，如果ROC值非常低或负值，可能表明市场过冷，价格可能会反弹。
        # dataframe['roc'] = ta.ROC(dataframe)

        # Overlap Studies
        # ------------------------------------


        #布林线的主要用途包括：
        #波动性分析：当价格接近上轨或下轨时，可能表明市场波动性增加。
        #买卖信号：价格突破上轨可能表示超买情况，是潜在的卖出信号；价格跌破下轨可能表示超卖情况，是潜在的买入信号。
        #趋势判断：当价格在中轨线之上时，可能表明上升趋势；在中轨线之下时，可能表明下降趋势。
        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe["bb_lowerband"] = bollinger["lower"]
        dataframe["bb_middleband"] = bollinger["mid"]
        dataframe["bb_upperband"] = bollinger["upper"]
        dataframe["bb_percent"] = (dataframe["close"] - dataframe["bb_lowerband"]) / (
            dataframe["bb_upperband"] - dataframe["bb_lowerband"]
        )
        dataframe["bb_width"] = (dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe[
            "bb_middleband"
        ]

        # Bollinger Bands - Weighted (EMA based instead of SMA)
        #在加权Bollinger Bands中，中间线是基于指数移动平均线（EMA）而不是SMA。这种变化使得中间线对最近的价格变动更加敏感。
        #加权Bollinger Bands由于对最近价格的加权，可能会比传统Bollinger Bands更敏感，但也可能导致更多的假信号。
        weighted_bollinger = qtpylib.weighted_bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe["wbb_upperband"] = weighted_bollinger["upper"]
        dataframe["wbb_lowerband"] = weighted_bollinger["lower"]
        dataframe["wbb_middleband"] = weighted_bollinger["mid"]
        dataframe["wbb_percent"] = (
            (dataframe["close"] - dataframe["wbb_lowerband"]) /
            (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"])
        )
        dataframe["wbb_width"] = (
            (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"]) /
            dataframe["wbb_middleband"]
        )

        # # EMA - Exponential Moving Average
        #EMA，即指数移动平均线 EMA相较于简单移动平均线（SMA）更加敏感，能够更快地反映价格的最新变化。
        dataframe['ema3'] = ta.EMA(dataframe, timeperiod=3)
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)

        # # SMA - Simple Moving Average
        # SMA，即简单移动平均线（Simple Moving Average）
        #计算特定时间周期内的平均价格来实现这一点
        # EMA（指数移动平均线）给予最近的价格更大的权重，因此对价格变动的反应速度比SMA快。
        # SMA对所有价格赋予相等的权重，因此更加稳定，但可能不如EMA敏感。
        # dataframe['sma3'] = ta.SMA(dataframe, timeperiod=3)
        # dataframe['sma5'] = ta.SMA(dataframe, timeperiod=5)
        # dataframe['sma10'] = ta.SMA(dataframe, timeperiod=10)
        # dataframe['sma21'] = ta.SMA(dataframe, timeperiod=21)
        # dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)
        # dataframe['sma100'] = ta.SMA(dataframe, timeperiod=100)

        # Parabolic SAR
        #可以作为潜在的止损或获利点。SAR指标特别适用于跟踪趋势并确定趋势可能停止或反转的点。
        dataframe["sar"] = ta.SAR(dataframe)

        # TEMA - Triple Exponential Moving Average
        #TEMA，即三重指数移动平均线（Triple Exponential Moving Average），是一种较少见但非常强大的趋势跟踪指标
        #更快的反应速度：由于TEMA是三次平滑的结果，它对价格变化的响应速度比单一EMA或SMA快。
        #减少滞后：TEMA的设计减少了传统EMA的滞后性，使其更贴近当前价格。
        #平滑性：TEMA提供了非常平滑的趋势线，有助于过滤掉市场的短期波动。
        dataframe["tema"] = ta.TEMA(dataframe, timeperiod=9)

        # Cycle Indicator
        # ------------------------------------
        # Hilbert Transform Indicator - SineWave
        #基于数学上的希尔伯特变换原理，用于金融时间序列分析，以生成瞬时指标，帮助交易者识别趋势的强度、趋势的开始和结束，以及潜在的转折点。
        #SineWave的正弦波形可以进入超买或超卖区域，这可以作为潜在的买卖信号。例如，当SineWave达到其上边界时，可能表明市场超买；当它达到下边界时，可能表明市场超卖。
        hilbert = ta.HT_SINE(dataframe)
        dataframe["htsine"] = hilbert["sine"]
        dataframe["htleadsine"] = hilbert["leadsine"]

        # Pattern Recognition - Bullish candlestick patterns
        # ------------------------------------
        # # Hammer: values [0, 100]
        #锤子线通常出现在下跌趋势的底部，具有小实体和长下影线。
        # dataframe['CDLHAMMER'] = ta.CDLHAMMER(dataframe)
        # # Inverted Hammer: values [0, 100]
        #   倒锤子线形态出现在上涨趋势的顶部，具有小实体和长上影线，可能预示着趋势的反转。
        #dataframe['CDLINVERTEDHAMMER'] = ta.CDLINVERTEDHAMMER(dataframe)
        # # Dragonfly Doji: values [0, 100]
        #蜻蜓十字星具有小实体位于蜡烛图的顶部，并且有很长的下影线，通常出现在下跌趋势的底部
        # dataframe['CDLDRAGONFLYDOJI'] = ta.CDLDRAGONFLYDOJI(dataframe)
        # # Piercing Line: values [0, 100]
        #刺透形态由一根阴线和一根阳线组成，阳线的实体从下方“刺透”阴线的实体，通常出现在下跌趋势的底部。
        # dataframe['CDLPIERCING'] = ta.CDLPIERCING(dataframe) # values [0, 100]
        # # Morningstar: values [0, 100]
        #晨星形态由三根蜡烛线组成，第一根是长阴线，第二根是十字星，第三根是长阳线，通常出现在下跌趋势的底部。
        # dataframe['CDLMORNINGSTAR'] = ta.CDLMORNINGSTAR(dataframe) # values [0, 100]
        # # Three White Soldiers: values [0, 100]
        #三白兵由三根依次上升的阳线组成，每根阳线的收盘价都高于前一根的收盘价，通常表示强烈的看涨趋势。
        # dataframe['CDL3WHITESOLDIERS'] = ta.CDL3WHITESOLDIERS(dataframe) # values [0, 100]

        # Pattern Recognition - Bearish candlestick patterns
        # ------------------------------------
        # # Hanging Man: values [0, 100]
        #上吊线出现在上升趋势的顶部，具有小实体和长下影线，上影线非常短或不存在。它预示着上升趋势可能即将结束。
        # dataframe['CDLHANGINGMAN'] = ta.CDLHANGINGMAN(dataframe)
        # # Shooting Star: values [0, 100]
        #射击之星具有小实体和长上影线，通常出现在上升趋势的顶部，表明买方的压力正在减弱。
        # dataframe['CDLSHOOTINGSTAR'] = ta.CDLSHOOTINGSTAR(dataframe)
        # # Gravestone Doji: values [0, 100]
        #墓碑十字星具有小实体位于蜡烛图的底部，并且有很长的上影线，通常出现在上升趋势的顶部。
        # dataframe['CDLGRAVESTONEDOJI'] = ta.CDLGRAVESTONEDOJI(dataframe)
        # # Dark Cloud Cover: values [0, 100]
        #乌云盖顶形态由两根蜡烛线组成，第一根是长阳线，第二根是阴线，其开盘价高于第一根的收盘价，但收盘价深入第一根阳线的实体内部，通常表示买方失去动能。
        # dataframe['CDLDARKCLOUDCOVER'] = ta.CDLDARKCLOUDCOVER(dataframe)
        # # Evening Doji Star: values [0, 100]
        #黄昏之星十字星由三根蜡烛线组成，第一根是长阳线，第二根是十字星，第三根是长阴线，通常表示上升趋势的结束。
        # dataframe['CDLEVENINGDOJISTAR'] = ta.CDLEVENINGDOJISTAR(dataframe)
        # # Evening Star: values [0, 100]
        #黄昏星形态与黄昏之星十字星类似，但第二根蜡烛线不必是十字星，可以是任何小实体的蜡烛线。
        # dataframe['CDLEVENINGSTAR'] = ta.CDLEVENINGSTAR(dataframe)

        # Pattern Recognition - Bullish/Bearish candlestick patterns
        #0：没有识别出特定的蜡烛图形态。
        #-100：识别出看跌的蜡烛图形态。
        #100：识别出看涨的蜡烛图形态。
        # ------------------------------------
        # # Three Line Strike: values [0, -100, 100]
        #表示在一个下跌趋势中出现一根长的阴线，紧接着是两根或更多的小实体蜡烛线，最后是一根长的阳线，这可能预示着趋势反转。
        # dataframe['CDL3LINESTRIKE'] = ta.CDL3LINESTRIKE(dataframe)
        # # Spinning Top: values [0, -100, 100]
        #纺锤顶形态具有小实体和长的上下影线，通常在价格连续移动后出现，表明市场不确定性和潜在的趋势变化。
        # dataframe['CDLSPINNINGTOP'] = ta.CDLSPINNINGTOP(dataframe) # values [0, -100, 100]
        # # Engulfing: values [0, -100, 100]
        #吞没形态由两根蜡烛线组成，第二根蜡烛线的实体完全覆盖第一根蜡烛线的实体，颜色与第一根相反，表明潜在的趋势反转。
        # dataframe['CDLENGULFING'] = ta.CDLENGULFING(dataframe) # values [0, -100, 100]
        # # Harami: values [0, -100, 100]
        #孕线形态与吞没形态类似，但第二根蜡烛线的实体更小，完全包含在第一根蜡烛线的实体内部，通常预示着趋势的减弱或反转。
        # dataframe['CDLHARAMI'] = ta.CDLHARAMI(dataframe) # values [0, -100, 100]
        # # Three Outside Up/Down: values [0, -100, 100]
        #三外形态是一个强烈的趋势反转信号，通常在强趋势的末端出现。在上升趋势的末端出现长阴线，而在下降趋势的末端出现长阳线。
        # dataframe['CDL3OUTSIDE'] = ta.CDL3OUTSIDE(dataframe) # values [0, -100, 100]
        # # Three Inside Up/Down: values [0, -100, 100]
        #三内形态与三外形态相反，它发生在趋势的末端，第一根是长蜡烛线，随后是两根逐渐变小的蜡烛线，最后是一根短蜡烛线，颜色与趋势相反。
        # dataframe['CDL3INSIDE'] = ta.CDL3INSIDE(dataframe) # values [0, -100, 100]

        # # Chart type
        # # ------------------------------------
        # # Heikin Ashi Strategy
        #Heikin Ashi是一种日本蜡烛图技术，旨在通过改变开盘价、收盘价、最高价和最低价来更清晰地展示市场趋势。  沒用
        # heikinashi = qtpylib.heikinashi(dataframe)
        # dataframe['ha_open'] = heikinashi['open']
        # dataframe['ha_close'] = heikinashi['close']
        # dataframe['ha_high'] = heikinashi['high']
        # dataframe['ha_low'] = heikinashi['low']

        # Retrieve best bid and best ask from the orderbook
        # ------------------------------------
        """
        # first check if dataprovider is available
        if self.dp:
            if self.dp.runmode.value in ('live', 'dry_run'):
                ob = self.dp.orderbook(metadata['pair'], 1)
                dataframe['best_bid'] = ob['bids'][0][0]
                dataframe['best_ask'] = ob['asks'][0][0]
        """

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        long_conditions = []
        short_conditions = []

        entry_long_1 = (
                ###当tema上穿波林下线 小于 ema10 小于 ema21
                qtpylib.crossed_above(dataframe["tema"],dataframe["bb_lowerband"])
                &
                (dataframe["tema"] < dataframe["ema10"])
                &
                (dataframe["tema"] < dataframe["ema21"])
                &
                (dataframe["volume"] > 0)
        )
        
        entry_long_2 = (
                ###当tema上穿波林中线 大于ema10 大于ema21
                qtpylib.crossed_above(dataframe["tema"],dataframe["bb_middleband"])
                &
                (dataframe["tema"] > dataframe["ema10"])
                &
                (dataframe["tema"] > dataframe["ema10"])
                &
                (dataframe["volume"] > 0)
        )

        long_conditions.append(entry_long_1)
        long_conditions.append(entry_long_2)

        if long_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, long_conditions), 'enter_long'] = 1

        entry_short_1 = (
            ## tema下穿波林上线 tema大于ema10 大于ema21
            qtpylib.crossed_below(dataframe["tema"],dataframe["bb_upperband"])
            &
            (dataframe["tema"] >= dataframe["ema10"])
            &
            (dataframe["tema"] >= dataframe["ema21"])
            &
            (dataframe["volume"] > 0)
        )
    
        entry_short_2 = (
            ## tema下穿波林中线 小于ema10 小于ema21 
            qtpylib.crossed_below(dataframe["tema"],dataframe["bb_middleband"])
            &
            (dataframe["tema"] < dataframe["ema10"])
            &
            (dataframe["tema"] < dataframe["ema10"])
            &
            (dataframe["volume"] > 0)
        )

        short_conditions.append(entry_short_1)
        short_conditions.append(entry_short_2)

        if short_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, short_conditions), 'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        exit_long_conditions = []
        exit_short_conditions = []

        exit_long_1 = (
            #当close大于波林上线的时候可以逃
            (dataframe['close'] > dataframe['bb_upperband'])
            & 
            (dataframe["volume"] > 0)  # 确保成交量不为 0
        )
        exit_long_conditions.append(exit_long_1)

        exit_long_2 = (
            (dataframe['tema'] > dataframe['bb_upperband'])
            &
            (dataframe["volume"] > 0)  # 确保成交量不为 0
        )
        exit_long_conditions.append(exit_long_2)
        if exit_long_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, exit_long_conditions), 'exit_long'] = 1

       
        exit_short_1 = (
            ## tema小于波林下线的时候逃
            (dataframe["tema"] <= dataframe["bb_lowerband"])
        
            &
            (dataframe["volume"] > 0)
        )
        
        exit_short_2 = (
            ## close小于波林下线的时候也可以逃
            (dataframe["close"] <= dataframe["bb_lowerband"])
        
            &
            (dataframe["volume"] > 0)
        )

        exit_short_conditions.append(exit_short_1)
        exit_short_conditions.append(exit_short_2)

        if exit_short_conditions:
            dataframe.loc[reduce(lambda x, y: x | y, exit_short_conditions), 'exit_short'] = 1

        return dataframe
    #定义杠杆倍率
    def leverage(self, pair: str, current_time: datetime, current_rate: float, proposed_leverage: float, max_leverage: float, entry_tag:str, side: str, **kwargs) -> float:
        """
        Customize leverage for each new trade. This method is only called in futures mode.

        :param pair: Pair that's currently analyzed
        :param current_time: datetime object, containing the current datetime
        :param current_rate: Rate, calculated based on pricing settings in exit_pricing.
        :param proposed_leverage: A leverage proposed by the bot.
        :param max_leverage: Max leverage allowed on this pair
        :param entry_tag: Optional entry_tag (buy_tag) if provided with the buy signal.
        :param side: 'long' or 'short' - indicating the direction of the proposed trade
        :return: A leverage amount, which is between 1.0 and max_leverage.
        """
        return 50.0