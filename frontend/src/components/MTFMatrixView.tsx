import React, { useEffect, useState } from 'react';
import {
  Grid3X3,
  Search,
  Layers,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Calendar,
  Clock,
} from 'lucide-react';
import { MTFMatrixResponse, MTFZoneRecord } from '../types/api';
import { api } from '../services/api';

const cleanDate = (d?: string | null) => {
  if (!d) return 'N/A';
  return d.split(' ')[0].split('T')[0];
};

const getTimeframePeriodLabel = (tf: string, dateStr: string) => {
  if (!dateStr || dateStr === 'N/A') return 'Base Confirmation';
  const parts = dateStr.split('-');
  const year = parts[0];
  const month = parseInt(parts[1] || '1', 10);

  if (tf === 'Yearly') {
    return `Secular Base (FY ${year})`;
  } else if (tf === 'Half-Yearly') {
    const half = month <= 6 ? 'H1' : 'H2';
    return `Macro Base (${half} ${year})`;
  } else if (tf === 'Quarterly') {
    const q = Math.ceil(month / 3);
    return `Quarterly Base (Q${q} ${year})`;
  } else if (tf === 'Monthly') {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `Monthly Base (${monthNames[month - 1] || ''} ${year})`;
  } else {
    return `Daily Confirmation Bar`;
  }
};

interface MTFMatrixViewProps {
  initialSymbol?: string;
  onInspectChart: (symbol: string) => void;
}

export const MTFMatrixView: React.FC<MTFMatrixViewProps> = ({
  initialSymbol = 'RELIANCE',
  onInspectChart,
}) => {
  const [symbol, setSymbol] = useState(initialSymbol);
  const [searchInput, setSearchInput] = useState('');
  const [data, setData] = useState<MTFMatrixResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    api.getMTFMatrix(symbol)
      .then((res) => {
        if (!isCancelled) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setError(err.message || 'No MTF matrix available');
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [symbol]);

  return (
    <div className="space-y-6">
      
      {/* Header Search & Symbol Controller */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
            <Grid3X3 className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black font-mono text-white">{symbol}</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                5-Timeframe Matrix
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Yearly, Half-Yearly, Quarterly, Monthly & Daily Dynamic Zones
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <input
              type="text"
              placeholder="Inspect symbol (e.g. TCS)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchInput.trim()) {
                  setSymbol(searchInput.trim().toUpperCase());
                  setSearchInput('');
                }
              }}
              className="pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-indigo-500 w-52"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
          </div>

          <button
            onClick={() => onInspectChart(symbol)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition"
          >
            Chart View
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="py-20 flex flex-col items-center justify-center gap-2 font-mono text-xs text-slate-400">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          Computing multi-timeframe nested matrix...
        </div>
      )}

      {error && (
        <div className="bg-rose-950/20 border border-rose-800/40 rounded-xl p-6 text-center font-mono text-xs text-rose-300">
          {error}
        </div>
      )}

      {data && !isLoading && (
        <div className="space-y-6">
          
          {/* Macro Curve & Alignment Summary Banner */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Macro Curve Location</div>
              <div className="text-2xl font-bold font-mono text-white mt-1">
                {data.macro_curve_location_pct.toFixed(1)}%
              </div>
              <div className="text-xs font-mono text-indigo-400 mt-1 font-semibold">
                Status: {data.macro_curve_status}
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Alignment Conviction</div>
              <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                {data.composite_alignment_conviction}
              </div>
              <div className="text-xs font-mono text-slate-400 mt-1">
                Current Market Price: ₹{data.current_price.toFixed(2)}
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Nested Super-Zones</div>
              <div className="text-2xl font-bold font-mono text-purple-400 mt-1">
                {data.nested_super_zones.length} Detected
              </div>
              <div className="text-xs font-mono text-slate-400 mt-1">
                Lower TF nested inside Higher TF demand
              </div>
            </div>

          </div>

          {/* Deep Understanding Executive Summary */}
          <div className="bg-indigo-950/20 border border-indigo-800/40 rounded-xl p-4 font-mono text-xs text-slate-200">
            <div className="text-indigo-400 uppercase text-[10px] font-bold tracking-wider mb-1 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> Institutional MTF Synthesis
            </div>
            {data.deep_understanding_summary}
          </div>

          {/* 5-Timeframe Active Zones Table */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
            <div className="px-4 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
              <div className="text-xs font-mono uppercase font-bold text-slate-300">
                Multi-Timeframe Zone Distribution (Yearly to Daily)
              </div>
              <div className="text-[11px] font-mono text-slate-400">
                {data.all_active_zones.length} Active Zones
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-4">Timeframe</th>
                    <th className="py-2.5 px-3">Pattern</th>
                    <th className="py-2.5 px-3 text-center text-indigo-400 font-bold bg-indigo-950/30 border-x border-indigo-900/40">
                      <div className="flex items-center justify-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Formation Date</span>
                      </div>
                    </th>
                    <th className="py-2.5 px-3 text-right">Proximal</th>
                    <th className="py-2.5 px-3 text-right">Distal</th>
                    <th className="py-2.5 px-3 text-right">Proximity %</th>
                    <th className="py-2.5 px-3">Freshness & Test Audit</th>
                    <th className="py-2.5 px-3 text-center">ML Prob</th>
                    <th className="py-2.5 px-3 text-center">Score</th>
                    <th className="py-2.5 px-4">Horizon Directive</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {data.all_active_zones.map((zone) => {
                    const isNested = zone.is_nested_in_htf;
                    const fDate = cleanDate(zone.formation_date);
                    const periodLabel = getTimeframePeriodLabel(zone.timeframe, fDate);
                    return (
                      <tr key={zone.zone_id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          <div className="flex items-center gap-2">
                            <span>{zone.timeframe}</span>
                            {isNested && (
                              <span className="px-1.5 py-0.5 rounded text-[9px] bg-purple-950 text-purple-300 border border-purple-800">
                                NESTED in {zone.nested_parent_timeframe}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px]">
                            {zone.pattern_type}
                          </span>
                        </td>
                        
                        {/* Dedicated Formation Date Column */}
                        <td className="py-3 px-3 text-center bg-indigo-950/15 border-x border-indigo-900/30">
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-700/60 font-bold font-mono text-xs shadow-sm">
                            <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                            <span>{fDate}</span>
                          </div>
                          <div className="text-[10px] text-slate-400 mt-1 font-mono">
                            {periodLabel}
                          </div>
                        </td>

                        <td className="py-3 px-3 text-right font-semibold text-emerald-400">
                          ₹{zone.proximal_line.toFixed(2)}
                        </td>
                        <td className="py-3 px-3 text-right text-rose-300">
                          ₹{zone.distal_line.toFixed(2)}
                        </td>
                        <td className="py-3 px-3 text-right">
                          <span className={zone.proximity_pct <= 3 ? 'text-emerald-400 font-bold' : 'text-slate-300'}>
                            {zone.proximity_pct.toFixed(2)}%
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <div className="text-slate-200 font-medium">
                            {zone.freshness_detail.replace(/ 00:00:00/g, '')}
                          </div>
                          <div className="text-[10px] text-slate-400 mt-0.5">
                            {zone.touch_count === 0 ? 'Pristine (Virgin)' : `Last Retest: ${cleanDate(zone.last_tested_date)}`}
                          </div>
                          {zone.tested_dates && zone.tested_dates.length > 0 && (
                            <div className="text-[9px] text-slate-500 mt-0.5 font-mono">
                              Retest Sessions: {zone.tested_dates.map((d) => cleanDate(d)).join(', ')}
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center text-emerald-400 font-bold">
                          {zone.ml_bounce_probability.toFixed(0)}%
                        </td>
                        <td className="py-3 px-3 text-center">
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-bold">
                            {zone.institutional_footprint_score.toFixed(0)}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-300 text-[11px]">
                          {zone.actionable_directive}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
