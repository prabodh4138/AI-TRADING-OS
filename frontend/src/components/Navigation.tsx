import React from 'react';
import {
  Target,
  LineChart,
  Grid3X3,
  Briefcase,
  BrainCircuit,
  BookOpen,
  Star,
} from 'lucide-react';

export type TabType = 'zones' | 'watchlist' | 'chart' | 'portfolio' | 'mtf' | 'thesis' | 'rulebook';

interface NavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  actionableCount: number;
  openPositionsCount: number;
  bestWatchlistCount: number;
  activeSymbol: string;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  onTabChange,
  actionableCount,
  openPositionsCount,
  bestWatchlistCount,
  activeSymbol,
}) => {
  const tabs = [
    {
      id: 'zones' as TabType,
      label: 'Institutional Demand Zones',
      icon: Target,
      badge: actionableCount > 0 ? `${actionableCount} Actionable` : undefined,
      badgeColor: 'bg-emerald-950 text-emerald-300 border-emerald-700/60',
    },
    {
      id: 'watchlist' as TabType,
      label: 'Best Stocks Watchlist',
      icon: Star,
      badge: bestWatchlistCount > 0 ? `${bestWatchlistCount} Curated` : 'Top Picks',
      badgeColor: 'bg-amber-950 text-amber-300 border-amber-700/60',
    },
    {
      id: 'chart' as TabType,
      label: 'Broker Chart Studio',
      icon: LineChart,
      badge: activeSymbol,
      badgeColor: 'bg-blue-950 text-blue-300 border-blue-700/60',
    },
    {
      id: 'portfolio' as TabType,
      label: 'Paper Trading Desk',
      icon: Briefcase,
      badge: openPositionsCount > 0 ? `${openPositionsCount} Active` : 'Auto-Trading Ready',
      badgeColor: 'bg-indigo-950 text-indigo-300 border-indigo-700/60',
    },
    {
      id: 'mtf' as TabType,
      label: 'Multi-Timeframe Matrix',
      icon: Grid3X3,
      badge: '5 Horizons',
      badgeColor: 'bg-purple-950 text-purple-300 border-purple-700/60',
    },
    {
      id: 'thesis' as TabType,
      label: '360° Stock Intelligence',
      icon: BrainCircuit,
      badge: 'Piotroski & Sentiment',
      badgeColor: 'bg-slate-800 text-slate-300 border-slate-700',
    },
    {
      id: 'rulebook' as TabType,
      label: 'GTF Master Rulebook',
      icon: BookOpen,
      badge: 'Master Spec v3.1',
      badgeColor: 'bg-slate-800 text-slate-300 border-slate-700',
    },
  ];

  return (
    <nav className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur px-4 lg:px-6">
      <div className="max-w-[1920px] mx-auto flex items-center gap-1 overflow-x-auto scrollbar-none py-1.5">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/40 shadow-sm shadow-blue-500/10 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent font-medium'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
              <span>{tab.label}</span>
              {tab.badge && (
                <span
                  className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${tab.badgeColor}`}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
