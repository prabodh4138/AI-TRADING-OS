"""CSV/JSON report export utilities."""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

def export_scan(df: pd.DataFrame, directory: str|Path="reports/output") -> Path:
    out=Path(directory); out.mkdir(parents=True,exist_ok=True); path=out/"latest_scan.csv"; df.to_csv(path,index=False); return path

def export_backtest(result, directory: str|Path="reports/output") -> Path:
    out=Path(directory); out.mkdir(parents=True,exist_ok=True); result.equity.to_csv(out/"equity_curve.csv",index=False); result.trades.to_csv(out/"trades.csv",index=False); (out/"metrics.json").write_text(json.dumps(result.metrics,indent=2,default=str),encoding="utf-8"); return out
