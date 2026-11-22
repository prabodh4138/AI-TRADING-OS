from data_engine.market_data import read_market_csv

def test_simple_csv():
    import tempfile
    from pathlib import Path
    p=Path(tempfile.mkdtemp())/"x.csv"
    p.write_text("SYMBOL,DATE,OPEN,HIGH,LOW,CLOSE,VOLUME\nABC,20-07-2026,10,12,9,11,1000\n",encoding="utf-8")
    x=read_market_csv(p)
    assert list(x.columns)==["symbol","trading_date","open","high","low","close","volume"]
    assert x.iloc[0].symbol=="ABC"
