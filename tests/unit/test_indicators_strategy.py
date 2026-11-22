import pandas as pd
import numpy as np
from indicator.calculator import IndicatorCalculator
from strategy.positional import PositionalStrategy
from risk.manager import RiskManager

def sample(n=260):
    d=pd.date_range("2025-01-01",periods=n,freq="B")
    close=np.linspace(100,220,n)+np.sin(np.arange(n)/7)*2
    return pd.DataFrame({"symbol":"TEST","trading_date":d.date,"open":close-1,"high":close+2,"low":close-2,"close":close,"volume":np.full(n,100000)})

def test_indicator_columns_and_no_talib_dependency():
    x=IndicatorCalculator().calculate(sample())
    for c in ["sma200","ema200","rsi14","macd","atr14","adx14","supertrend","trend_score","momentum_score"]: assert c in x
    assert x.iloc[-1]["sma200"]>0

def test_strategy_is_deterministic():
    x=IndicatorCalculator().calculate(sample()).iloc[-1]
    a=PositionalStrategy().evaluate(x); b=PositionalStrategy().evaluate(x)
    assert a==b

def test_risk_sizing():
    plan=RiskManager(risk_per_trade_pct=1).size(100000,100,95,110)
    assert plan.quantity==200
    assert round(plan.risk_amount,2)==1000
