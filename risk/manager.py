"""Position sizing and portfolio risk controls."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PositionPlan:
    quantity: int
    entry: float
    stop: float
    target: float
    risk_amount: float
    position_value: float

class RiskManager:
    def __init__(self, max_positions: int = 20, risk_per_trade_pct: float = 1.0, max_portfolio_risk_pct: float = 10.0):
        self.max_positions=max_positions; self.risk_per_trade_pct=risk_per_trade_pct; self.max_portfolio_risk_pct=max_portfolio_risk_pct
    def size(self, capital: float, entry: float, stop: float, target: float, current_positions: int = 0) -> PositionPlan:
        if capital<=0 or entry<=0 or stop<=0 or target<=entry: raise ValueError("Invalid capital/entry/stop/target")
        if current_positions>=self.max_positions: raise ValueError("Maximum positions reached")
        risk_per_share=entry-stop
        allowed_risk=min(capital*self.risk_per_trade_pct/100, capital*self.max_portfolio_risk_pct/100)
        qty=int(allowed_risk//risk_per_share)
        if qty<1: raise ValueError("Capital is insufficient for one risk-sized share")
        return PositionPlan(qty,entry,stop,target,qty*risk_per_share,qty*entry)
