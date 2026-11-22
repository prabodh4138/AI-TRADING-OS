"""Dependency-light technical indicator calculator.

Uses pandas/numpy only so AI-TOS does not depend on native TA-Lib wheels.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

class IndicatorCalculator:
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        required = {"trading_date","open","high","low","close","volume"}
        missing = required - set(df.columns)
        if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
        x = df.copy().sort_values("trading_date").reset_index(drop=True)
        c,h,l,v = [pd.to_numeric(x[k], errors="coerce") for k in ("close","high","low","volume")]
        for n in (20,50,100,200): x[f"sma{n}"] = c.rolling(n, min_periods=n).mean()
        for n in (9,20,50,100,200): x[f"ema{n}"] = c.ewm(span=n, adjust=False, min_periods=n).mean()
        delta = c.diff(); gain=delta.clip(lower=0); loss=-delta.clip(upper=0)
        avg_gain=gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean(); avg_loss=loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
        rs=avg_gain/avg_loss.replace(0,np.nan); x["rsi14"]=(100-(100/(1+rs))).fillna(100).where(avg_loss.ne(0),100)
        ema12=c.ewm(span=12,adjust=False,min_periods=12).mean(); ema26=c.ewm(span=26,adjust=False,min_periods=26).mean(); x["macd"]=ema12-ema26; x["macd_signal"]=x["macd"].ewm(span=9,adjust=False,min_periods=9).mean(); x["macd_histogram"]=x["macd"]-x["macd_signal"]
        prev=c.shift(1); tr=pd.concat([(h-l),(h-prev).abs(),(l-prev).abs()],axis=1).max(axis=1); x["atr14"]=tr.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
        mid=c.rolling(20,min_periods=20).mean(); std=c.rolling(20,min_periods=20).std(ddof=0); x["bb_middle"]=mid; x["bb_upper"]=mid+2*std; x["bb_lower"]=mid-2*std
        up=h.diff(); down=-l.diff(); plus=np.where((up>down)&(up>0),up,0.0); minus=np.where((down>up)&(down>0),down,0.0); atr=x["atr14"]
        plus_di=100*pd.Series(plus,index=x.index).ewm(alpha=1/14,adjust=False,min_periods=14).mean()/atr.replace(0,np.nan); minus_di=100*pd.Series(minus,index=x.index).ewm(alpha=1/14,adjust=False,min_periods=14).mean()/atr.replace(0,np.nan); dx=100*(plus_di-minus_di).abs()/(plus_di+minus_di).replace(0,np.nan); x["plus_di"]=plus_di; x["minus_di"]=minus_di; x["adx14"]=dx.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
        x["obv"]=(np.sign(c.diff()).fillna(0)*v).cumsum(); x["volume_sma20"]=v.rolling(20,min_periods=20).mean(); x["relative_volume"]=v/x["volume_sma20"].replace(0,np.nan)
        x["roc10"]=c.pct_change(10)*100; x["momentum10"]=c.diff(10)
        low14=l.rolling(14,min_periods=14).min(); high14=h.rolling(14,min_periods=14).max(); x["stochastic_k"]=100*(c-low14)/(high14-low14).replace(0,np.nan); x["stochastic_d"]=x["stochastic_k"].rolling(3,min_periods=3).mean()
        x = self._supertrend(x)
        x["trend_score"] = self._trend_score(x); x["momentum_score"] = self._momentum_score(x)
        return x

    @staticmethod
    def _supertrend(x: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        h,l,c,atr=x.high,x.low,x.close,x.atr14
        hl2=(h+l)/2; upper=(hl2+multiplier*atr).copy(); lower=(hl2-multiplier*atr).copy(); fu=upper.copy(); fl=lower.copy(); st=pd.Series(np.nan,index=x.index); direction=pd.Series(np.nan,index=x.index)
        for i in range(1,len(x)):
            fu.iloc[i]=upper.iloc[i] if pd.isna(fu.iloc[i-1]) or upper.iloc[i]<fu.iloc[i-1] or c.iloc[i-1]>fu.iloc[i-1] else fu.iloc[i-1]
            fl.iloc[i]=lower.iloc[i] if pd.isna(fl.iloc[i-1]) or lower.iloc[i]>fl.iloc[i-1] or c.iloc[i-1]<fl.iloc[i-1] else fl.iloc[i-1]
            if pd.isna(atr.iloc[i]): continue
            if pd.isna(st.iloc[i-1]): direction.iloc[i]=1 if c.iloc[i]>=hl2.iloc[i] else -1
            elif direction.iloc[i-1] == -1: direction.iloc[i]=1 if c.iloc[i]>fu.iloc[i] else -1
            else: direction.iloc[i]=-1 if c.iloc[i]<fl.iloc[i] else 1
            st.iloc[i]=fl.iloc[i] if direction.iloc[i]==1 else fu.iloc[i]
        x["supertrend"]=st; x["supertrend_direction"]=direction
        return x

    @staticmethod
    def _trend_score(x: pd.DataFrame) -> pd.Series:
        score=pd.Series(0.0,index=x.index); score += (x.close>x.ema20).astype(float); score += (x.ema20>x.ema50).astype(float); score += (x.ema50>x.ema200).astype(float); score += (x.supertrend_direction>0).astype(float); score += (x.adx14>20).astype(float); return score/5*100
    @staticmethod
    def _momentum_score(x: pd.DataFrame) -> pd.Series:
        score=pd.Series(0.0,index=x.index); score += ((x.rsi14>=50)&(x.rsi14<=70)).astype(float); score += (x.macd_histogram>0).astype(float); score += (x.relative_volume>=1).astype(float); score += (x.roc10>0).astype(float); score += (x.stochastic_k>x.stochastic_d).astype(float); return score/5*100
