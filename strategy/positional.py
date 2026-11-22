"""Rule-based positional strategy. Deterministic, explainable and backtestable."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True, slots=True)
class Signal:
    symbol: str
    trading_date: object
    action: str
    score: float
    entry: float
    stop: float | None
    target: float | None
    reasons: tuple[str, ...]

class PositionalStrategy:
    def __init__(self, min_score: float = 70.0, atr_stop: float = 2.0, rr: float = 2.0):
        self.min_score, self.atr_stop, self.rr = min_score, atr_stop, rr
    def evaluate(self, row: pd.Series) -> Signal:
        score=0.0; reasons=[]
        checks=[(row.get("close",0)>row.get("ema20",float("inf")),20,"Price above EMA20"),(row.get("ema20",0)>row.get("ema50",float("inf")),20,"EMA20 above EMA50"),(row.get("ema50",0)>row.get("ema200",float("inf")),15,"EMA50 above EMA200"),(row.get("supertrend_direction",-1)>0,15,"SuperTrend bullish"),(row.get("adx14",0)>=20,10,"ADX confirms trend"),(50<=row.get("rsi14",0)<=70,10,"RSI in bullish range"),(row.get("macd_histogram",0)>0,5,"MACD histogram positive"),(row.get("relative_volume",0)>=1,5,"Relative volume supports move")]
        for ok,pts,why in checks:
            if ok: score+=pts; reasons.append(why)
        entry=float(row["close"]); atr=float(row.get("atr14",0) or 0); stop=entry-self.atr_stop*atr if atr>0 else None; target=entry+(entry-stop)*self.rr if stop else None
        action="BUY" if score>=self.min_score else "WATCH"
        return Signal(str(row.get("symbol","")),row.get("trading_date"),action,score,entry,stop,target,tuple(reasons))
