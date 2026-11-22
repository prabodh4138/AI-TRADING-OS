import React, { useState } from 'react';
import { X, CheckCircle2, AlertCircle, Award, Target, ShieldCheck, Zap, Sparkles } from 'lucide-react';
import { ZoneCandidate } from '../types/api';
import { Master123ChecklistView } from './Master123ChecklistView';

interface ScorecardModalProps {
  candidate: ZoneCandidate | null;
  onClose: () => void;
  onExecute: (candidate: ZoneCandidate) => void;
}

export const ScorecardModal: React.FC<ScorecardModalProps> = ({
  candidate,
  onClose,
  onExecute,
}) => {
  const [activeTab, setActiveTab] = useState<'12_POINT' | '123_MASTER'>('12_POINT');

  if (!candidate) return null;

  const score = candidate.institutional_score_100;
  const scoreColor =
    score >= 80 ? 'text-emerald-400 border-emerald-500/40 bg-emerald-950/40' :
    score >= 65 ? 'text-blue-400 border-blue-500/40 bg-blue-950/40' :
    'text-amber-400 border-amber-500/40 bg-amber-950/40';

  const defaultChecklist = [
    { item: 'Valid Institutional Structure (DBR / RBR pattern with clear base)', passed: true, note: candidate.zone_type },
    { item: 'Freshness Status (Unbreached, Max 2 touches)', passed: candidate.touch_count <= 2, note: candidate.freshness_detail },
    { item: 'Exact Testing Audit (Historical test date recorded)', passed: candidate.touch_count === 0 || candidate.last_tested_date !== 'N/A', note: candidate.last_tested_date },
    { item: 'HTF Trend Alignment (Yearly / Quarterly / Monthly not opposing)', passed: candidate.yearly_trend.includes('BULLISH'), note: `Y: ${candidate.yearly_trend}` },
    { item: 'Location on Macro Curve (At or Below Equilibrium)', passed: candidate.curve_location_pct <= 60, note: `${candidate.curve_location_pct}% (${candidate.curve_state})` },
    { item: 'Strict Reward-to-Risk (Minimum 2.0:1 institutional standard)', passed: candidate.reward_to_risk >= 2.0, note: `${candidate.reward_to_risk.toFixed(1)}:1` },
    { item: 'Risk Per Trade Limit (Zone width within 3.0% limit)', passed: candidate.risk_pct <= 3.0, note: `${candidate.risk_pct.toFixed(2)}%` },
    { item: 'Displacement Ratio (Strong exit candle with ATR displacement)', passed: candidate.displacement_ratio_atr >= 1.2, note: `${candidate.displacement_ratio_atr.toFixed(2)}x ATR` },
    { item: 'Liquidity Sweep Confirmation (Prior low purged)', passed: candidate.has_liquidity_sweep, note: candidate.sweep_description },
    { item: 'Hard Risk Gate Status (No pending sector/macro blocks)', passed: candidate.gate_passed, note: candidate.hard_gate_status },
    { item: 'Volatility-Buffered Stop-Loss Defined', passed: true, note: `₹${candidate.buffered_stop_loss.toFixed(2)}` },
    { item: '360° Fundamental & Sentiment Support', passed: (candidate.conviction_score_360 ?? 50) >= 50, note: `${candidate.fundamental_tier ?? 'AVERAGE'}` },
  ];

  const checklist = candidate.checklist_12_points && candidate.checklist_12_points.length > 0
    ? candidate.checklist_12_points
    : defaultChecklist;

  const passedCount = checklist.filter((c) => c.passed).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
              <Award className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-white font-mono">{candidate.symbol}</h3>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {candidate.zone_type}
                </span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                  {candidate.location_state}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Institutional Qualification Audit & GTF Master Confluence
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* View Tab Toggle */}
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-1">
              <button
                onClick={() => setActiveTab('12_POINT')}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition ${
                  activeTab === '12_POINT'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                12-Pt GTF Gates
              </button>
              <button
                onClick={() => setActiveTab('123_MASTER')}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold flex items-center gap-1.5 transition ${
                  activeTab === '123_MASTER'
                    ? 'bg-purple-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-300" />
                123-Point Master Matrix
              </button>
            </div>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {activeTab === '123_MASTER' ? (
            <Master123ChecklistView symbol={candidate.symbol} />
          ) : (
            <>
              {/* Top Score Banner */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            
            {/* 100-Pt Score */}
            <div className={`p-4 rounded-xl border flex flex-col items-center justify-center text-center ${scoreColor}`}>
              <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Institutional Score
              </div>
              <div className="text-3xl font-black font-mono">
                {score.toFixed(0)} <span className="text-lg font-normal text-slate-400">/ 100</span>
              </div>
              <div className="text-[11px] font-mono mt-1 font-semibold">
                Tier: {candidate.conviction_tier} (Grade {candidate.alignment_grade})
              </div>
            </div>

            {/* Reward to Risk */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/40 flex flex-col items-center justify-center text-center">
              <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Reward / Risk
              </div>
              <div className="text-2xl font-bold font-mono text-emerald-400">
                {candidate.reward_to_risk.toFixed(1)} : 1
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">
                Target: ₹{candidate.target_supply.toFixed(2)}
              </div>
            </div>

            {/* Freshness Audit */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/40 flex flex-col items-center justify-center text-center">
              <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Freshness & Tests
              </div>
              <div className="text-lg font-bold font-mono text-blue-400">
                {candidate.freshness}
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">
                {candidate.touch_count === 0 ? 'Never Tested (Pristine)' : `Tested on: ${candidate.last_tested_date}`}
              </div>
            </div>

            {/* 12-Pt Qualification */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/40 flex flex-col items-center justify-center text-center">
              <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Checklist Audit
              </div>
              <div className="text-2xl font-bold font-mono text-purple-400">
                {passedCount} / {checklist.length}
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">
                {passedCount >= 10 ? 'INSTITUTIONAL READY' : 'CONDITIONAL'}
              </div>
            </div>
          </div>

          {/* Pricing Geometry */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
            <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-3 flex items-center gap-2">
              <Target className="w-4 h-4 text-blue-400" />
              Zone Execution Boundaries & Buffer Rules
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-[10px]">CURRENT PRICE (CMP)</div>
                <div className="text-base font-bold text-white mt-0.5">₹{candidate.current_price.toFixed(2)}</div>
              </div>
              <div className="p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-800/40">
                <div className="text-emerald-400 text-[10px]">PROXIMAL LINE (ENTRY)</div>
                <div className="text-base font-bold text-emerald-300 mt-0.5">₹{candidate.proximal_line.toFixed(2)}</div>
              </div>
              <div className="p-2.5 rounded-lg bg-rose-950/30 border border-rose-800/40">
                <div className="text-rose-400 text-[10px]">DISTAL LINE (BASE)</div>
                <div className="text-base font-bold text-rose-300 mt-0.5">₹{candidate.distal_line.toFixed(2)}</div>
              </div>
              <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/40">
                <div className="text-amber-400 text-[10px]">BUFFERED STOP LOSS</div>
                <div className="text-base font-bold text-amber-300 mt-0.5">₹{candidate.buffered_stop_loss.toFixed(2)}</div>
              </div>
            </div>
          </div>

          {/* 12-Point Checklist Table */}
          <div>
            <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Institutional 12-Point Qualification Checklist
            </h4>
            <div className="border border-slate-800 rounded-xl overflow-hidden">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-4 w-12">Status</th>
                    <th className="py-2.5 px-4">Inspection Criterion</th>
                    <th className="py-2.5 px-4 text-right">Audited Measurement</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                  {checklist.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition">
                      <td className="py-2.5 px-4">
                        {item.passed ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-amber-400" />
                        )}
                      </td>
                      <td className="py-2.5 px-4 font-sans text-slate-200">
                        {item.item}
                      </td>
                      <td className="py-2.5 px-4 text-right text-slate-400 font-mono">
                        {item.note}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Institutional Rational */}
          <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-300 space-y-2">
            <div className="text-slate-400 uppercase text-[10px] tracking-wider font-bold">
              Entry Execution Model & Footprint Rationale
            </div>
            <div className="flex items-center gap-2 text-blue-300">
              <Zap className="w-4 h-4" />
              <span className="font-semibold">{candidate.recommended_entry_model}:</span>
              <span>{candidate.entry_model_rational}</span>
            </div>
            <div className="text-slate-400 text-[11px]">
              BOS Type: <span className="text-slate-200">{candidate.bos_type}</span> | 
              Displacement: <span className="text-slate-200">{candidate.displacement_ratio_atr.toFixed(2)}x ATR</span> | 
              Odds Enhancer Score: <span className="text-slate-200">{candidate.odds_enhancer_score.toFixed(1)} / 10</span>
            </div>
          </div>
          </>
          )}

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="text-xs text-slate-400 font-mono">
            {candidate.is_actionable ? '🟢 Actionable Setup' : '🟡 Priority Watchlist Setup'}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition"
            >
              Close
            </button>
            <button
              onClick={() => {
                onExecute(candidate);
                onClose();
              }}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white text-xs font-mono font-semibold transition shadow-lg shadow-emerald-600/20"
            >
              Execute Paper Trade (CMP ₹{candidate.current_price.toFixed(2)})
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
