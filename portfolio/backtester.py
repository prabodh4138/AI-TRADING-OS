"""Simple no-lookahead daily backtester for the positional strategy."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from strategy.positional import PositionalStrategy
from risk.manager import RiskManager

@dataclass(frozen=True, slots=True)
class BacktestResult:
    equity: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str,float]

class PositionalBacktester:
    def __init__(self, strategy=None, risk=None): self.strategy=strategy or PositionalStrategy(); self.risk=risk or RiskManager()
    def run(self, data: pd.DataFrame, capital: float=1_000_000) -> BacktestResult:
        if data.empty: return BacktestResult(pd.DataFrame(),pd.DataFrame(),{})
        x=data.copy().sort_values("trading_date").reset_index(drop=True); cash=float(capital); qty=0; entry=stop=target=0.0; rows=[]; trades=[]
        for i,row in x.iterrows():
            if qty:
                exit_price=None; reason=None
                if float(row.low)<=stop: exit_price=stop; reason="STOP"
                elif float(row.high)>=target: exit_price=target; reason="TARGET"
                if exit_price is not None:
                    pnl=qty*(exit_price-entry); cash+=qty*exit_price; trades.append({"entry_date":entry_date,"exit_date":row.trading_date,"entry":entry,"exit":exit_price,"qty":qty,"pnl":pnl,"reason":reason}); qty=0
            if qty==0 and i < len(x)-1:
                sig=self.strategy.evaluate(row)
                if sig.action=="BUY" and sig.stop and sig.target:
                    try:
                        plan=self.risk.size(cash,sig.entry,sig.stop,sig.target)
                    except ValueError: plan=None
                    if plan:
                        qty=plan.quantity; entry=sig.entry; stop=sig.stop; target=sig.target; entry_date=row.trading_date; cash-=qty*entry
            mark=cash+qty*float(row.close); rows.append({"trading_date":row.trading_date,"equity":mark,"cash":cash,"position_value":qty*float(row.close)})
        equity=pd.DataFrame(rows); trades_df=pd.DataFrame(trades); metrics=self._metrics(equity,trades_df,capital); return BacktestResult(equity,trades_df,metrics)
    @staticmethod
    def _metrics(eq,trades,capital):
        if eq.empty: return {}
        ret=float(eq.equity.iloc[-1]/capital-1); peak=eq.equity.cummax(); dd=eq.equity/peak-1; wins=trades[trades.pnl>0] if not trades.empty else trades
        return {"initial_capital":capital,"final_equity":float(eq.equity.iloc[-1]),"return_pct":ret*100,"max_drawdown_pct":float(dd.min()*100),"trades":float(len(trades)),"win_rate_pct":float(len(wins)/len(trades)*100) if len(trades) else 0.0}
