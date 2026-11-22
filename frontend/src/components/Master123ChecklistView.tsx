import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Award,
  Layers,
  Search,
  Filter,
  TrendingUp,
  FileText,
  BarChart2,
  Activity,
  Globe,
  DollarSign,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { Master123Response, MasterChecklistItem } from '../types/api';
import { api } from '../services/api';

interface Master123ChecklistViewProps {
  symbol: string;
  onClose?: () => void;
  compact?: boolean;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  Fundamental: <Award className="w-3.5 h-3.5" />,
  Technical: <TrendingUp className="w-3.5 h-3.5" />,
  Sector: <Activity className="w-3.5 h-3.5" />,
  Institutional: <DollarSign className="w-3.5 h-3.5" />,
  News: <FileText className="w-3.5 h-3.5" />,
  Global: <Globe className="w-3.5 h-3.5" />,
  Market: <BarChart2 className="w-3.5 h-3.5" />,
  Volume: <Layers className="w-3.5 h-3.5" />,
  Risk: <ShieldCheck className="w-3.5 h-3.5" />,
  Execution: <Zap className="w-3.5 h-3.5" />,
};

export const Master123ChecklistView: React.FC<Master123ChecklistViewProps> = ({
  symbol,
  onClose,
  compact = false,
}) => {
  const [data, setData] = useState<Master123Response | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'PASSED' | 'FAILED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    api
      .getMasterChecklist(symbol)
      .then((res) => {
        if (!isCancelled) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setError(err.message || 'Failed to load Master 123 checklist');
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [symbol]);

  if (isLoading) {
    return (
      <div className="p-8 flex flex-col items-center justify-center space-y-3 bg-slate-900/60 border border-slate-800 rounded-xl">
        <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono text-slate-400">
          Running 123-Parameter Institutional Confluence Audit for {symbol}...
        </span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl text-center space-y-2">
        <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
        <div className="text-sm font-mono text-white font-bold">123-Point Audit Unavailable</div>
        <div className="text-xs font-mono text-slate-400">{error || 'Data could not be retrieved.'}</div>
      </div>
    );
  }

  // Filter items
  const filteredItems = data.all_123_items.filter((item) => {
    const matchesCat = activeCategory === 'ALL' || item.category.toLowerCase() === activeCategory.toLowerCase();
    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'PASSED' && item.passed) ||
      (statusFilter === 'FAILED' && !item.passed);
    const q = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !q ||
      item.parameter.toLowerCase().includes(q) ||
      item.preferred_criteria.toLowerCase().includes(q) ||
      item.actual_value.toLowerCase().includes(q) ||
      item.audit_note.toLowerCase().includes(q);
    return matchesCat && matchesStatus && matchesSearch;
  });

  const tierColors: Record<string, string> = {
    AAA_SECULAR_COMPOUNDER: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/50',
    AA_STRONG_CONVICTION: 'bg-blue-950/80 text-blue-300 border-blue-500/50',
    A_QUALIFIED: 'bg-indigo-950/80 text-indigo-300 border-indigo-500/50',
    CONDITIONAL: 'bg-amber-950/80 text-amber-300 border-amber-500/50',
  };

  const badgeColor = tierColors[data.institutional_tier] || 'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <div className="space-y-5">
      {/* Top Audit Master Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-bold font-mono text-white">{data.symbol}</h3>
                <span className="text-xs font-mono text-slate-400">({data.company_name})</span>
                <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
                  {data.institutional_tier}
                </span>
                {data.hard_gate_cleared ? (
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800">
                    HARD GATES CLEARED
                  </span>
                ) : (
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-800">
                    GATE WARNING
                  </span>
                )}
              </div>
              <p className="text-xs font-mono text-slate-400 mt-1">
                Institutional Master 123-Point Confluence & Qualification Specification (10 Categories)
              </p>
            </div>
          </div>

          {/* Aggregate Pass Counter */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">
                Audit Pass Rate
              </div>
              <div className="text-2xl font-black font-mono text-emerald-400">
                {data.total_score_123} <span className="text-sm font-normal text-slate-500">/ {data.max_score_123}</span>
                <span className="ml-2 text-sm text-purple-300 font-bold">({data.composite_pass_rate_pct}%)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Strengths and Red Flags */}
        <div className="mt-4 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="space-y-1">
            <div className="text-[10px] font-mono uppercase font-bold text-emerald-400 tracking-wider flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Key Institutional Strengths
            </div>
            <div className="flex flex-wrap gap-1.5">
              {data.key_strengths.map((str, idx) => (
                <span
                  key={idx}
                  className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-800/40"
                >
                  {str}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-[10px] font-mono uppercase font-bold text-amber-400 tracking-wider flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              Audited Risk Factors / Disclaimers
            </div>
            <div className="flex flex-wrap gap-1.5">
              {data.key_red_flags.map((flag, idx) => (
                <span
                  key={idx}
                  className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-950/40 text-amber-300 border border-amber-800/40"
                >
                  {flag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 10 Category Breakdown Cards */}
      {!compact && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
          {data.category_summaries.map((cat) => {
            const isSelected = activeCategory.toLowerCase() === cat.category.toLowerCase();
            const passPct = cat.pass_rate_pct;
            const barColor =
              passPct >= 90 ? 'bg-emerald-500' : passPct >= 75 ? 'bg-blue-500' : 'bg-amber-500';

            return (
              <button
                key={cat.category}
                onClick={() => setActiveCategory(isSelected ? 'ALL' : cat.category)}
                className={`p-2.5 rounded-xl border text-left transition ${
                  isSelected
                    ? 'bg-purple-950/40 border-purple-500 text-white shadow-lg'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-semibold flex items-center gap-1.5 truncate">
                    {CATEGORY_ICONS[cat.category] || null}
                    {cat.category}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 font-bold">
                    {cat.grade}
                  </span>
                </div>
                <div className="mt-2 flex items-baseline justify-between text-[11px] font-mono">
                  <span className="text-slate-400 font-medium">
                    {cat.passed_items}/{cat.total_items}
                  </span>
                  <span className="font-bold text-emerald-400">{cat.pass_rate_pct}%</span>
                </div>
                <div className="mt-1 w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${barColor} rounded-full transition-all duration-300`}
                    style={{ width: `${cat.pass_rate_pct}%` }}
                  />
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Filter and Search Controls */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {/* Category Pill 'ALL' */}
          <button
            onClick={() => setActiveCategory('ALL')}
            className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition ${
              activeCategory === 'ALL'
                ? 'bg-purple-600 text-white shadow-md'
                : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            All Categories ({data.max_score_123})
          </button>

          {/* Quick Status Filters */}
          <div className="h-4 w-px bg-slate-700 mx-1 hidden sm:block" />
          <button
            onClick={() => setStatusFilter('ALL')}
            className={`px-2.5 py-1 rounded text-xs font-mono transition ${
              statusFilter === 'ALL' ? 'bg-slate-700 text-white font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            All Status
          </button>
          <button
            onClick={() => setStatusFilter('PASSED')}
            className={`px-2.5 py-1 rounded text-xs font-mono flex items-center gap-1 transition ${
              statusFilter === 'PASSED'
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-700 font-bold'
                : 'text-slate-400 hover:text-emerald-300'
            }`}
          >
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            Passed ({data.total_score_123})
          </button>
          <button
            onClick={() => setStatusFilter('FAILED')}
            className={`px-2.5 py-1 rounded text-xs font-mono flex items-center gap-1 transition ${
              statusFilter === 'FAILED'
                ? 'bg-rose-950 text-rose-300 border border-rose-700 font-bold'
                : 'text-slate-400 hover:text-rose-300'
            }`}
          >
            <AlertCircle className="w-3 h-3 text-rose-400" />
            Flags ({data.max_score_123 - data.total_score_123})
          </button>
        </div>

        {/* Search Input */}
        <div className="relative min-w-[200px] flex-1 max-w-xs">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search parameter, metric, criteria..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      {/* Detailed Checklist Audit Table */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/40">
        <div className="overflow-x-auto max-h-[550px] overflow-y-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 sticky top-0 z-10 text-slate-400 uppercase text-[10px] border-b border-slate-800 tracking-wider">
              <tr>
                <th className="py-2.5 px-3 w-12 text-center">#</th>
                <th className="py-2.5 px-3 w-28">Category</th>
                <th className="py-2.5 px-4">Parameter to Check</th>
                <th className="py-2.5 px-4">Preferred Criteria / Signal</th>
                <th className="py-2.5 px-4">Audited Measurement</th>
                <th className="py-2.5 px-3 w-24 text-center">Verdict</th>
                <th className="py-2.5 px-4">Audit Note</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/30">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 font-mono">
                    No checklist items match the current filters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr
                    key={item.sl_no}
                    className={`hover:bg-slate-800/40 transition ${
                      !item.passed ? 'bg-amber-950/10' : ''
                    }`}
                  >
                    <td className="py-2 px-3 text-center text-slate-500 font-semibold">
                      {item.sl_no}
                    </td>
                    <td className="py-2 px-3">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-300">
                        {CATEGORY_ICONS[item.category] || null}
                        {item.category}
                      </span>
                    </td>
                    <td className="py-2 px-4 font-sans font-medium text-slate-200">
                      {item.parameter}
                    </td>
                    <td className="py-2 px-4 text-slate-300 font-mono text-[11px]">
                      {item.preferred_criteria}
                    </td>
                    <td className="py-2 px-4 font-mono font-semibold text-white text-[11px]">
                      {item.actual_value}
                    </td>
                    <td className="py-2 px-3 text-center">
                      {item.passed ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 text-[10px] font-bold">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          PASS
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/60 text-[10px] font-bold">
                          <AlertCircle className="w-3 h-3 text-amber-400" />
                          FLAG
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-4 text-slate-400 text-[11px] font-mono">
                      {item.audit_note}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
