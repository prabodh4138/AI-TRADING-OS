import React, { useEffect, useRef, useState, useMemo } from 'react';
import {
  LineChart,
  Search,
  Zap,
  Target,
  Maximize2,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Sliders,
  TrendingUp,
  Activity,
  CheckCircle2,
  Eye,
  Calendar,
} from 'lucide-react';
import { CandleBar, CandleHistoryResponse, ChartZoneOverlay } from '../types/api';
import { api } from '../services/api';

interface ChartStudioProps {
  initialSymbol?: string;
  onExecuteTrade: (symbol: string, entry: number, sl: number, target: number, qty?: number) => void;
}

export const ChartStudio: React.FC<ChartStudioProps> = ({
  initialSymbol = 'RELIANCE',
  onExecuteTrade,
}) => {
  const [symbol, setSymbol] = useState<string>(initialSymbol);
  const [timeframe, setTimeframe] = useState<string>('1D');
  const [chartType, setChartType] = useState<'candles' | 'hollow' | 'line'>('candles');

  // Indicators toggles
  const [showEMA20, setShowEMA20] = useState<boolean>(true);
  const [showEMA50, setShowEMA50] = useState<boolean>(true);
  const [showSMA200, setShowSMA200] = useState<boolean>(false);
  const [showVolume, setShowVolume] = useState<boolean>(true);
  const [showZones, setShowZones] = useState<boolean>(true);

  // Zoom / visible bars control
  const [visibleBarsCount, setVisibleBarsCount] = useState<number>(60);

  const [searchInput, setSearchInput] = useState<string>('');
  const [symbolsList, setSymbolsList] = useState<string[]>([]);
  const [data, setData] = useState<CandleHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Position Sizing Calculator state
  const [riskPct, setRiskPct] = useState<number>(1.5);
  const [customQty, setCustomQty] = useState<number>(0);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [hoveredBar, setHoveredBar] = useState<CandleBar | null>(null);

  // Load symbol list on mount
  useEffect(() => {
    api.getSymbols()
      .then((res) => {
        setSymbolsList(res);
      })
      .catch(() => {});
  }, []);

  // Sync initialSymbol if changed
  useEffect(() => {
    if (initialSymbol) {
      setSymbol(initialSymbol);
    }
  }, [initialSymbol]);

  // Load candle data when symbol or timeframe changes
  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    api.getSymbolBars(symbol, timeframe)
      .then((res) => {
        if (!isCancelled) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setError(err.message || 'Failed to load historical bars');
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [symbol, timeframe]);

  // Active Zone calculations
  const activeZone = useMemo(() => {
    if (!data?.zones || data.zones.length === 0) return null;
    return data.zones[0];
  }, [data]);

  // Calculate recommended shares from 1.5% risk
  const calculatedQty = useMemo(() => {
    if (!data) return 100;
    const entry = activeZone ? activeZone.proximal_line : data.current_price;
    const sl = activeZone ? activeZone.buffered_stop_loss : entry * 0.98;
    const riskPerShare = Math.max(1.0, entry - sl);
    const totalCapital = 1000000;
    const riskCapital = totalCapital * (riskPct / 100.0);
    return Math.max(1, Math.floor(riskCapital / riskPerShare));
  }, [data, activeZone, riskPct]);

  // High-performance Broker-Grade Canvas Renderer
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data || data.bars.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.parentElement?.clientWidth || 800;
    const height = 520;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    ctx.scale(dpr, dpr);

    const padding = { top: 25, right: 80, bottom: showVolume ? 90 : 45, left: 15 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const volumeHeight = showVolume ? 60 : 0;
    const volumeTop = height - volumeHeight - 25;

    // Background
    ctx.fillStyle = '#080c14';
    ctx.fillRect(0, 0, width, height);

    // Visible subset based on zoom
    const bars = data.bars.slice(-visibleBarsCount);
    if (bars.length === 0) return;

    let minPrice = Math.min(...bars.map((b) => b.low));
    let maxPrice = Math.max(...bars.map((b) => b.high));

    if (showZones && activeZone) {
      minPrice = Math.min(minPrice, activeZone.buffered_stop_loss * 0.99);
      maxPrice = Math.max(maxPrice, activeZone.target_supply * 1.01);
    }

    const priceRange = maxPrice - minPrice || 1;
    const priceToY = (price: number) =>
      padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;

    // Grid lines & Price Axis
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    const steps = 6;
    for (let i = 0; i <= steps; i++) {
      const y = padding.top + (chartHeight / steps) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartWidth, y);
      ctx.stroke();

      const priceVal = maxPrice - (priceRange / steps) * i;
      ctx.fillStyle = '#64748b';
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`₹${priceVal.toFixed(1)}`, padding.left + chartWidth + 8, y + 3);
    }

    // Render Institutional Zone Band Overlay
    if (showZones && activeZone) {
      const proximalY = priceToY(activeZone.proximal_line);
      const distalY = priceToY(activeZone.distal_line);
      const stopY = priceToY(activeZone.buffered_stop_loss);
      const targetY = priceToY(activeZone.target_supply);

      // Shaded Demand Zone Fill
      ctx.fillStyle = 'rgba(16, 185, 129, 0.12)';
      ctx.fillRect(padding.left, Math.min(proximalY, distalY), chartWidth, Math.abs(distalY - proximalY));

      // Proximal Line (Entry)
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(padding.left, proximalY);
      ctx.lineTo(padding.left + chartWidth, proximalY);
      ctx.stroke();

      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 9px JetBrains Mono, monospace';
      ctx.fillText(`PROX ₹${activeZone.proximal_line.toFixed(1)}`, padding.left + chartWidth + 8, proximalY + 3);

      // Distal Line (Base)
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(padding.left, distalY);
      ctx.lineTo(padding.left + chartWidth, distalY);
      ctx.stroke();

      ctx.fillStyle = '#f43f5e';
      ctx.fillText(`DIST ₹${activeZone.distal_line.toFixed(1)}`, padding.left + chartWidth + 8, distalY + 3);

      // Volatility Buffered Stop Loss
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1.2;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(padding.left, stopY);
      ctx.lineTo(padding.left + chartWidth, stopY);
      ctx.stroke();

      ctx.fillStyle = '#ef4444';
      ctx.fillText(`SL ₹${activeZone.buffered_stop_loss.toFixed(1)}`, padding.left + chartWidth + 8, stopY + 3);

      // Target Supply Line
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(padding.left, targetY);
      ctx.lineTo(padding.left + chartWidth, targetY);
      ctx.stroke();

      ctx.fillStyle = '#3b82f6';
      ctx.fillText(`TARGET ₹${activeZone.target_supply.toFixed(1)}`, padding.left + chartWidth + 8, targetY + 3);

      ctx.setLineDash([]);
    }

    // Render EMA Indicators
    const drawIndicatorLine = (field: 'ema20' | 'ema50' | 'sma200', color: string, widthPx = 1.5) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = widthPx;
      ctx.beginPath();
      let started = false;

      bars.forEach((bar, idx) => {
        const val = bar[field];
        if (val !== undefined && val !== null) {
          const x = padding.left + idx * (chartWidth / bars.length) + (chartWidth / bars.length) / 2;
          const y = priceToY(val);
          if (!started) {
            ctx.moveTo(x, y);
            started = true;
          } else {
            ctx.lineTo(x, y);
          }
        }
      });
      ctx.stroke();
    };

    if (showEMA20) drawIndicatorLine('ema20', '#38bdf8', 1.5);
    if (showEMA50) drawIndicatorLine('ema50', '#fb923c', 1.5);
    if (showSMA200) drawIndicatorLine('sma200', '#a855f7', 1.8);

    // Render Candlesticks or Line Chart
    const barWidth = Math.max(2, chartWidth / bars.length - 2.5);

    if (chartType === 'line') {
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.beginPath();
      bars.forEach((bar, idx) => {
        const x = padding.left + idx * (chartWidth / bars.length) + (chartWidth / bars.length) / 2;
        const y = priceToY(bar.close);
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    } else {
      bars.forEach((bar, idx) => {
        const x = padding.left + idx * (chartWidth / bars.length) + (chartWidth / bars.length) / 2;
        const openY = priceToY(bar.open);
        const closeY = priceToY(bar.close);
        const highY = priceToY(bar.high);
        const lowY = priceToY(bar.low);

        const isGreen = bar.close >= bar.open;
        const color = isGreen ? '#10b981' : '#ef4444';

        // Wick
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(x, highY);
        ctx.lineTo(x, lowY);
        ctx.stroke();

        // Body
        const bodyTop = Math.min(openY, closeY);
        const bodyHeight = Math.max(2, Math.abs(closeY - openY));

        if (chartType === 'hollow' && isGreen) {
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.2;
          ctx.strokeRect(x - barWidth / 2, bodyTop, barWidth, bodyHeight);
        } else {
          ctx.fillStyle = color;
          ctx.fillRect(x - barWidth / 2, bodyTop, barWidth, bodyHeight);
        }

        // Date labels on axis
        if (idx % Math.max(6, Math.floor(bars.length / 8)) === 0 || idx === bars.length - 1) {
          ctx.fillStyle = '#64748b';
          ctx.font = '9px JetBrains Mono, monospace';
          ctx.textAlign = 'center';
          ctx.fillText(bar.time.slice(5), x, height - 10);
        }
      });
    }

    // Render Volume Bars Histogram
    if (showVolume) {
      const maxVol = Math.max(...bars.map((b) => b.volume)) || 1;
      bars.forEach((bar, idx) => {
        const x = padding.left + idx * (chartWidth / bars.length) + (chartWidth / bars.length) / 2;
        const vH = (bar.volume / maxVol) * volumeHeight;
        const y = volumeTop + volumeHeight - vH;
        const isGreen = bar.close >= bar.open;

        ctx.fillStyle = isGreen ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)';
        ctx.fillRect(x - barWidth / 2, y, barWidth, vH);
      });
    }

  }, [data, activeZone, timeframe, chartType, showEMA20, showEMA50, showSMA200, showVolume, showZones, visibleBarsCount]);

  // Handle Canvas mousemove for tooltip
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !data || data.bars.length === 0) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;

    const padding = { top: 25, right: 80, bottom: 45, left: 15 };
    const chartWidth = rect.width - padding.left - padding.right;
    const bars = data.bars.slice(-visibleBarsCount);

    const barIdx = Math.floor(((x - padding.left) / chartWidth) * bars.length);
    if (barIdx >= 0 && barIdx < bars.length) {
      setHoveredBar(bars[barIdx]);
    } else {
      setHoveredBar(null);
    }
  };

  const filteredSymbols = symbolsList
    .filter((s) => s.toLowerCase().includes(searchInput.toLowerCase()))
    .slice(0, 15);

  const isPositive = (data?.current_change_pct ?? 0) >= 0;

  return (
    <div className="space-y-3">
      
      {/* Broker Floating Top Command Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-md">
        
        {/* Symbol Search & Live Price HUD */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <input
              type="text"
              placeholder="Search symbol (e.g. TCS)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-blue-500 w-44"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            
            {searchInput && filteredSymbols.length > 0 && (
              <div className="absolute left-0 mt-1 w-44 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl z-20 max-h-48 overflow-y-auto">
                {filteredSymbols.map((s) => (
                  <button
                    key={s}
                    onClick={() => {
                      setSymbol(s);
                      setSearchInput('');
                    }}
                    className="w-full text-left px-3 py-1.5 text-xs font-mono text-slate-200 hover:bg-blue-600 hover:text-white transition"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xl font-black font-mono text-white tracking-wide">{symbol}</span>
            {data && (
              <div className="flex items-center gap-2 font-mono">
                <span className="text-base font-extrabold text-white">
                  ₹{data.current_price.toFixed(2)}
                </span>
                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                  isPositive ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'
                }`}>
                  {isPositive ? '+' : ''}{data.current_change_pct.toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Timeframe Selector (1D, 1W, 1M, 1Q) */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          {(['1D', '1W', '1M', '1Q'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition ${
                timeframe === tf
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {/* Chart Style (Candles, Hollow, Line) */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-mono">
          <button
            onClick={() => setChartType('candles')}
            className={`px-2 py-1 rounded ${chartType === 'candles' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Candles
          </button>
          <button
            onClick={() => setChartType('hollow')}
            className={`px-2 py-1 rounded ${chartType === 'hollow' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Hollow
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`px-2 py-1 rounded ${chartType === 'line' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Line
          </button>
        </div>

        {/* Indicators Toolbar Toggle */}
        <div className="flex items-center gap-1 text-[11px] font-mono">
          <button
            onClick={() => setShowEMA20(!showEMA20)}
            className={`px-2 py-1 rounded border transition ${
              showEMA20 ? 'bg-sky-950/80 text-sky-300 border-sky-600/60 font-bold' : 'text-slate-500 border-slate-800'
            }`}
          >
            EMA 20
          </button>

          <button
            onClick={() => setShowEMA50(!showEMA50)}
            className={`px-2 py-1 rounded border transition ${
              showEMA50 ? 'bg-amber-950/80 text-amber-300 border-amber-600/60 font-bold' : 'text-slate-500 border-slate-800'
            }`}
          >
            EMA 50
          </button>

          <button
            onClick={() => setShowSMA200(!showSMA200)}
            className={`px-2 py-1 rounded border transition ${
              showSMA200 ? 'bg-purple-950/80 text-purple-300 border-purple-600/60 font-bold' : 'text-slate-500 border-slate-800'
            }`}
          >
            SMA 200
          </button>

          <button
            onClick={() => setShowZones(!showZones)}
            className={`px-2 py-1 rounded border transition ${
              showZones ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600/60 font-bold' : 'text-slate-500 border-slate-800'
            }`}
          >
            GTF Zones
          </button>

          <button
            onClick={() => setShowVolume(!showVolume)}
            className={`px-2 py-1 rounded border transition ${
              showVolume ? 'bg-slate-800 text-slate-200 border-slate-700 font-bold' : 'text-slate-500 border-slate-800'
            }`}
          >
            Volume
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setVisibleBarsCount((c) => Math.max(25, c - 15))}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setVisibleBarsCount((c) => Math.min(250, c + 25))}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setVisibleBarsCount(60)}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

      {/* Main Chart Canvas & Broker Order Terminal Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        
        {/* Main Chart Window */}
        <div
          ref={containerRef}
          className="lg:col-span-3 bg-slate-900/70 border border-slate-800 rounded-xl p-4 relative overflow-hidden"
        >
          {isLoading && (
            <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center z-10 font-mono text-xs text-blue-400 gap-2">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              Loading {symbol} {timeframe} candles...
            </div>
          )}

          {error && (
            <div className="p-8 text-center text-rose-400 font-mono text-xs">
              {error}
            </div>
          )}

          {/* Broker Live Floating HUD */}
          <div className="h-7 flex items-center justify-between text-[11px] font-mono text-slate-400 mb-2 border-b border-slate-800/80 pb-1">
            <div className="flex items-center gap-3">
              {hoveredBar ? (
                <>
                  <span className="text-white font-bold">{hoveredBar.time}</span>
                  <span>O: <span className="text-slate-200">₹{hoveredBar.open.toFixed(2)}</span></span>
                  <span>H: <span className="text-emerald-400">₹{hoveredBar.high.toFixed(2)}</span></span>
                  <span>L: <span className="text-rose-400">₹{hoveredBar.low.toFixed(2)}</span></span>
                  <span>C: <span className="text-slate-200 font-bold">₹{hoveredBar.close.toFixed(2)}</span></span>
                  <span>Vol: <span className="text-slate-300">{hoveredBar.volume.toLocaleString()}</span></span>
                  {hoveredBar.ema20 && (
                    <span className="text-sky-400">EMA20: ₹{hoveredBar.ema20.toFixed(1)}</span>
                  )}
                  {hoveredBar.ema50 && (
                    <span className="text-amber-400">EMA50: ₹{hoveredBar.ema50.toFixed(1)}</span>
                  )}
                </>
              ) : (
                <>
                  <span className="text-slate-300 font-semibold">{symbol} ({timeframe})</span>
                  {data && (
                    <>
                      <span>52W High: <strong className="text-emerald-400">₹{data.high_52w.toFixed(2)}</strong></span>
                      <span>52W Low: <strong className="text-rose-400">₹{data.low_52w.toFixed(2)}</strong></span>
                    </>
                  )}
                </>
              )}
            </div>

            <div className="text-[10px] text-slate-500">
              Showing {visibleBarsCount} bars • Scroll/Zoom supported
            </div>
          </div>

          <canvas
            ref={canvasRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setHoveredBar(null)}
            className="w-full cursor-crosshair rounded-lg"
          />

          {/* Institutional Legend */}
          <div className="flex items-center gap-4 text-[10px] font-mono text-slate-400 mt-2 pt-2 border-t border-slate-800/60">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-emerald-500 inline-block" /> Proximal Line (Entry)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-rose-500 inline-block" /> Distal Line (Base)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-red-500 border-dashed border-b border-red-500 inline-block" /> Volatility Buffered Stop Loss
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-blue-500 inline-block" /> Target Opposing Supply
            </span>
            {showEMA20 && <span className="text-sky-400">• EMA 20</span>}
            {showEMA50 && <span className="text-amber-400">• EMA 50</span>}
            {showSMA200 && <span className="text-purple-400">• SMA 200</span>}
          </div>
        </div>

        {/* Right Sidebar: Broker-Style Quick Order Terminal (Zerodha Kite / TradingView style) */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between space-y-4 shadow-xl">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white font-bold">
                <Zap className="w-4 h-4 text-emerald-400" />
                Broker Order Terminal
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                PAPER BUY
              </span>
            </div>

            {/* Pricing Parameters */}
            <div className="space-y-2.5 font-mono text-xs">
              <div className="p-2 rounded bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400 text-[10px]">CURRENT PRICE</span>
                <span className="font-bold text-white">₹{data?.current_price.toFixed(2) ?? '---'}</span>
              </div>

              {activeZone && (
                <div className="p-2 rounded bg-indigo-950/30 border border-indigo-800/50 flex justify-between items-center">
                  <span className="text-indigo-400 text-[10px] flex items-center gap-1 font-bold">
                    <Calendar className="w-3 h-3 text-indigo-400" />
                    FORMATION DATE
                  </span>
                  <span className="font-bold text-indigo-300 font-mono">
                    {activeZone.formation_date ? activeZone.formation_date.split(' ')[0] : 'N/A'}
                  </span>
                </div>
              )}

              <div className="p-2 rounded bg-emerald-950/20 border border-emerald-800/40 flex justify-between items-center">
                <span className="text-emerald-400 text-[10px]">PROXIMAL ENTRY</span>
                <span className="font-bold text-emerald-300">
                  ₹{activeZone ? activeZone.proximal_line.toFixed(2) : (data?.current_price.toFixed(2) ?? '---')}
                </span>
              </div>

              <div className="p-2 rounded bg-rose-950/20 border border-rose-800/40 flex justify-between items-center">
                <span className="text-rose-400 text-[10px]">BUFFERED STOP LOSS</span>
                <span className="font-bold text-rose-300">
                  ₹{activeZone ? activeZone.buffered_stop_loss.toFixed(2) : ((data?.current_price ?? 0) * 0.98).toFixed(2)}
                </span>
              </div>

              <div className="p-2 rounded bg-blue-950/20 border border-blue-800/40 flex justify-between items-center">
                <span className="text-blue-400 text-[10px]">TARGET SUPPLY (2.5R)</span>
                <span className="font-bold text-blue-300">
                  ₹{activeZone ? activeZone.target_supply.toFixed(2) : ((data?.current_price ?? 0) * 1.06).toFixed(2)}
                </span>
              </div>
            </div>

            {/* Position Sizing Calculator */}
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2 font-mono text-xs">
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-[10px] text-slate-400 uppercase">Capital at Risk</span>
                <div className="flex items-center gap-1">
                  {[1.0, 1.5, 2.0].map((pct) => (
                    <button
                      key={pct}
                      onClick={() => setRiskPct(pct)}
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        riskPct === pct ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {pct}%
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-[11px]">Calculated Shares:</span>
                <span className="font-extrabold text-white text-sm">{calculatedQty} shares</span>
              </div>

              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Position Value:</span>
                <span className="text-slate-200">
                  ₹{((data?.current_price ?? 0) * calculatedQty).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>
          </div>

          {/* Execution Button */}
          <div>
            <button
              onClick={() => {
                if (data && activeZone) {
                  onExecuteTrade(
                    symbol,
                    activeZone.proximal_line,
                    activeZone.buffered_stop_loss,
                    activeZone.target_supply,
                    calculatedQty
                  );
                } else if (data) {
                  onExecuteTrade(
                    symbol,
                    data.current_price,
                    data.current_price * 0.98,
                    data.current_price * 1.05,
                    calculatedQty
                  );
                }
              }}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-mono text-xs font-black transition shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4" />
              <span>BUY {symbol} ({calculatedQty} QTY)</span>
            </button>
            <div className="text-[9px] text-slate-500 text-center font-mono mt-2">
              Protected by Volatility-Buffered SL & GTF Dynamic Trailing
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
