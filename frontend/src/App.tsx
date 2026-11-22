import React, { useEffect, useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Navigation, TabType } from './components/Navigation';
import { ZonesView } from './components/ZonesView';
import { WatchlistView } from './components/WatchlistView';
import { ChartStudio } from './components/ChartStudio';
import { MTFMatrixView } from './components/MTFMatrixView';
import { PortfolioView } from './components/PortfolioView';
import { StockThesisView } from './components/StockThesisView';
import { RulebookView } from './components/RulebookView';
import { ScorecardModal } from './components/ScorecardModal';
import { useWebSocket } from './hooks/useWebSocket';
import { api } from './services/api';
import {
  AutoTradeStatus,
  MarketStatus,
  PortfolioSummary,
  ZoneCandidate,
  ZoneScanResponse,
} from './types/api';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('zones');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');
  
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [autoTradeStatus, setAutoTradeStatus] = useState<AutoTradeStatus | null>(null);
  const [scanData, setScanData] = useState<ZoneScanResponse | null>(null);
  const [curatedCount, setCuratedCount] = useState<number>(15);

  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isPortfolioLoading, setIsPortfolioLoading] = useState<boolean>(false);

  const [inspectingCandidate, setInspectingCandidate] = useState<ZoneCandidate | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  // Load Market Status (Live Health & Posture)
  const loadMarketStatus = useCallback(async () => {
    try {
      const data = await api.getMarketStatus();
      setMarketStatus(data);
    } catch (e) {
      console.error('Failed to load market status', e);
    }
  }, []);

  // Load Portfolio Summary (Cash, Equity, Win Rate, Positions)
  const loadPortfolio = useCallback(async () => {
    try {
      setIsPortfolioLoading(true);
      const data = await api.getPortfolioSummary();
      setPortfolio(data);
    } catch (e) {
      console.error('Failed to load portfolio', e);
    } finally {
      setIsPortfolioLoading(false);
    }
  }, []);

  // Load Auto-Trading Status
  const loadAutoTradeStatus = useCallback(async () => {
    try {
      const data = await api.getAutoTradeStatus();
      setAutoTradeStatus(data);
    } catch (e) {
      console.error('Failed to load auto trade status', e);
    }
  }, []);

  // Load GTF Scan Data
  const loadZoneScan = useCallback(async (forceRefresh = false) => {
    try {
      setIsScanning(true);
      const data = await api.getZoneScan(forceRefresh);
      setScanData(data);
    } catch (e) {
      console.error('Failed to load zone scan', e);
    } finally {
      setIsScanning(false);
    }
  }, []);

  const refreshAll = useCallback(() => {
    loadMarketStatus();
    loadPortfolio();
    loadAutoTradeStatus();
    loadZoneScan();
  }, [loadMarketStatus, loadPortfolio, loadAutoTradeStatus, loadZoneScan]);

  // Initial load and Continuous Reactive Background Sync (Every 4s)
  useEffect(() => {
    refreshAll();
    const timer = setInterval(() => {
      loadMarketStatus();
      loadPortfolio();
      loadAutoTradeStatus();
    }, 4000);

    return () => clearInterval(timer);
  }, [refreshAll, loadMarketStatus, loadPortfolio, loadAutoTradeStatus]);

  // WebSocket Integration for real-time reactivity
  const { isConnected } = useWebSocket((msg) => {
    if (msg.event === 'TRADE_EXECUTED' || msg.event === 'BATCH_TRADES_EXECUTED') {
      loadPortfolio();
      showNotification('Paper trading position executed successfully!');
    } else if (msg.event === 'AUTO_TRADE_CYCLE_COMPLETED') {
      loadPortfolio();
      loadAutoTradeStatus();
      showNotification(`Auto-Trade cycle: ${msg.new_opened ?? 0} entered, ${msg.closed ?? 0} closed.`);
    } else if (msg.event === 'PIPELINE_COMPLETED' || msg.event === 'MARKET_DATA_UPDATED') {
      refreshAll();
    }
  });

  // Trade Execution Handlers
  const handleExecuteCandidate = async (candidate: ZoneCandidate) => {
    try {
      await api.executeTrade({
        symbol: candidate.symbol,
        entry_trigger: candidate.proximal_line,
        stop_loss: candidate.buffered_stop_loss,
        target_zone: candidate.target_supply,
        gate_reason: `GTF Setup: ${candidate.zone_type} | Tier: ${candidate.conviction_tier}`,
      });
      showNotification(`Executed buy order for ${candidate.symbol} at ₹${candidate.proximal_line.toFixed(2)}`);
      loadPortfolio();
    } catch (err: any) {
      showNotification(`Trade rejected: ${err.message}`, 'error');
    }
  };

  const handleExecuteDirect = async (sym: string, entry: number, sl: number, target: number, qty?: number) => {
    try {
      await api.executeTrade({
        symbol: sym,
        entry_trigger: entry,
        stop_loss: sl,
        target_zone: target,
        position_size_shares: qty,
        gate_reason: `Broker Terminal Manual Execution`,
      });
      showNotification(`Executed order for ${sym}: Entry ₹${entry.toFixed(2)} | SL ₹${sl.toFixed(2)} | Target ₹${target.toFixed(2)}`);
      loadPortfolio();
    } catch (err: any) {
      showNotification(`Trade rejected: ${err.message}`, 'error');
    }
  };

  const handleInspectChart = (symbol: string) => {
    setSelectedSymbol(symbol);
    setActiveTab('chart');
  };

  const handleInspectThesis = (symbol: string) => {
    setSelectedSymbol(symbol);
    setActiveTab('thesis');
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      
      {/* Toast Notification */}
      {notification && (
        <div className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl border flex items-center gap-3 shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom duration-300 ${
          notification.type === 'success'
            ? 'bg-emerald-950/90 border-emerald-600 text-emerald-200'
            : 'bg-rose-950/90 border-rose-600 text-rose-200'
        }`}>
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-400" />
          )}
          <span className="text-xs font-mono font-medium">{notification.message}</span>
          <button onClick={() => setNotification(null)} className="ml-2 font-bold text-slate-400 hover:text-white">×</button>
        </div>
      )}

      {/* Institutional Top Header (Live Updating) */}
      <Header
        marketStatus={marketStatus}
        portfolio={portfolio}
        autoTradeStatus={autoTradeStatus}
        isConnected={isConnected}
        onRefresh={refreshAll}
        onAutoTradeTriggered={() => loadPortfolio()}
      />

      {/* Navigation Sub-Header (Dynamic Badges) */}
      <Navigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        actionableCount={scanData?.at_demand_count ?? 0}
        openPositionsCount={portfolio?.open_positions_count ?? 0}
        bestWatchlistCount={curatedCount}
        activeSymbol={selectedSymbol}
      />

      {/* Main Tab Views Container */}
      <main className="flex-1 max-w-[1920px] w-full mx-auto p-4 lg:p-6">
        {activeTab === 'zones' && (
          <ZonesView
            scanData={scanData}
            isLoading={isScanning}
            onSelectCandidate={(c) => {
              setSelectedSymbol(c.symbol);
            }}
            onInspectScorecard={(c) => setInspectingCandidate(c)}
            onExecuteTrade={handleExecuteCandidate}
            onInspectChart={handleInspectChart}
            onInspectThesis={handleInspectThesis}
          />
        )}

        {activeTab === 'watchlist' && (
          <WatchlistView
            onInspectChart={handleInspectChart}
            onInspectThesis={handleInspectThesis}
            onExecuteTrade={(sym, entry, sl, target) => handleExecuteDirect(sym, entry, sl, target)}
          />
        )}

        {activeTab === 'chart' && (
          <ChartStudio
            initialSymbol={selectedSymbol}
            onExecuteTrade={handleExecuteDirect}
          />
        )}

        {activeTab === 'portfolio' && (
          <PortfolioView
            portfolio={portfolio}
            autoTradeStatus={autoTradeStatus}
            isLoading={isPortfolioLoading}
            onRefresh={loadPortfolio}
            onInspectChart={handleInspectChart}
          />
        )}

        {activeTab === 'mtf' && (
          <MTFMatrixView
            initialSymbol={selectedSymbol}
            onInspectChart={handleInspectChart}
          />
        )}

        {activeTab === 'thesis' && (
          <StockThesisView
            initialSymbol={selectedSymbol}
            onInspectChart={handleInspectChart}
          />
        )}

        {activeTab === 'rulebook' && (
          <RulebookView />
        )}
      </main>

      {/* Scorecard Modal */}
      <ScorecardModal
        candidate={inspectingCandidate}
        onClose={() => setInspectingCandidate(null)}
        onExecute={handleExecuteCandidate}
      />

      {/* Bottom Institutional Status Bar */}
      <footer className="border-t border-slate-900 bg-slate-950/80 px-4 py-2 text-[11px] font-mono text-slate-500 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span>AI Trading OS v3.1</span>
          <span>•</span>
          <span className="text-slate-400">GTF Institutional Dynamic Engine</span>
          <span>•</span>
          <span className="text-emerald-500">Auto-Trading & Broker Canvas Live</span>
        </div>
        <div className="text-slate-500">
          🔒 Simulated Paper Trading Only • Real-time Mark-to-Market & Trailing Stops Active
        </div>
      </footer>

    </div>
  );
};
export default App;
