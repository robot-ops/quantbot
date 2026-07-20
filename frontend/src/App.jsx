import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import MetricsCard from './components/MetricsCard';
import ChartView from './components/ChartView';
import TradeHistory from './components/TradeHistory';
import SettingsModal from './components/SettingsModal';
import ErrorBoundary from './components/ErrorBoundary';
import { Terminal } from 'lucide-react';
import axios from 'axios';

// Dynamic API Base & WebSocket URL (Auto switch between Localhost and Cloud Render)
const DEFAULT_CLOUD_API = 'https://quantbot-i0ab.onrender.com';
const isLocalhost = typeof window !== 'undefined' && window.location.hostname === 'localhost';

const API_BASE = import.meta.env.VITE_API_BASE || (isLocalhost ? 'http://localhost:8000' : DEFAULT_CLOUD_API);
const WS_URL = import.meta.env.VITE_WS_URL || (isLocalhost ? 'ws://localhost:8000/ws' : DEFAULT_CLOUD_API.replace('https://', 'wss://').replace('http://', 'ws://') + '/ws');

export default function App() {
  const [stats, setStats] = useState(null);
  const [candles, setCandles] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const wsRef = useRef(null);
  const logsContainerRef = useRef(null);

  // Fetch Initial Data
  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/status`);
      setStats(res.data);
    } catch (e) {
      // Backend offline or starting up
    }
  };

  const fetchCandles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/chart/candles`);
      if (res.data?.candles) {
        setCandles(res.data.candles);
      }
    } catch (e) {
      // Backend offline or starting up
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchCandles();

    let isMounted = true;
    let ws = null;
    let reconnectTimer = null;

    // Graceful WebSocket Connection
    const connectWS = () => {
      if (!isMounted) return;
      try {
        ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          // Connected
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            if (data.stats) setStats(data.stats);
            if (data.tick?.price) {
              setCandles(prev => {
                if (prev.length === 0) return prev;
                const last = { ...prev[prev.length - 1] };
                last.close = data.tick.price;
                if (data.tick.price > last.high) last.high = data.tick.price;
                if (data.tick.price < last.low) last.low = data.tick.price;
                return [...prev.slice(0, -1), last];
              });
            }
          } catch (err) {
            // JSON parse ignore
          }
        };

        ws.onerror = () => {
          // Suppress raw WebSocket error log
        };

        ws.onclose = () => {
          if (isMounted) {
            reconnectTimer = setTimeout(connectWS, 3000);
          }
        };
      } catch (e) {
        if (isMounted) {
          reconnectTimer = setTimeout(connectWS, 3000);
        }
      }
    };

    connectWS();

    return () => {
      isMounted = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) {
        ws.onclose = null;
        if (ws.readyState === WebSocket.CONNECTING) {
          ws.onopen = () => {
            try { ws.close(); } catch (e) {}
          };
        } else if (ws.readyState === WebSocket.OPEN) {
          try { ws.close(); } catch (e) {}
        }
      }
    };
  }, []);

  // Auto-scroll terminal logs container to top when new entry arrives
  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop = 0;
    }
  }, [stats?.logs]);

  const handleStart = async () => {
    // Optimistic UI Update for instant responsiveness
    setStats(prev => prev ? { ...prev, is_running: true } : prev);
    try {
      await axios.post(`${API_BASE}/api/control/start`);
      fetchStatus();
    } catch (e) {
      alert(`Gagal menjalankan bot. Pastikan backend sudah berjalan di ${API_BASE}`);
      fetchStatus();
    }
  };

  const handleStop = async () => {
    // Optimistic UI Update for instant responsiveness
    setStats(prev => prev ? { ...prev, is_running: false } : prev);
    try {
      await axios.post(`${API_BASE}/api/control/stop`);
      fetchStatus();
    } catch (e) {
      alert('Gagal menghentikan bot.');
      fetchStatus();
    }
  };

  const handleToggleMode = async () => {
    if (!stats) return;
    const currentMode = stats.trading_mode;
    const newMode = currentMode === 'demo' ? 'live' : 'demo';

    if (newMode === 'live') {
      const confirmLive = window.confirm('⚠️ PERINGATAN LIVE TRADING:\nApakah Anda yakin ingin berpindah ke Mode Live Trading? Bot akan mengeksekusi order asli di Tokocrypto.');
      if (!confirmLive) return;
    }

    setStats(prev => prev ? { ...prev, trading_mode: newMode } : prev);
    try {
      await axios.post(`${API_BASE}/api/settings/update`, { trading_mode: newMode });
      fetchStatus();
    } catch (e) {
      alert('Gagal mengubah mode trading.');
      fetchStatus();
    }
  };

  const handleResetDemo = async () => {
    if (window.confirm('Reset saldo Paper Trading kembali ke $10,000 USD virtual?')) {
      try {
        await axios.post(`${API_BASE}/api/control/reset-demo`);
        fetchStatus();
      } catch (e) {
        alert('Gagal reset demo.');
      }
    }
  };

  const handleSaveSettings = async (newConfig) => {
    try {
      await axios.post(`${API_BASE}/api/settings/update`, newConfig);
      fetchStatus();
      fetchCandles();
    } catch (e) {
      alert('Gagal menyimpan pengaturan.');
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px 16px' }}>
      {/* Header Bar */}
      <Header
        stats={stats}
        onStart={handleStart}
        onStop={handleStop}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onToggleMode={handleToggleMode}
      />

      {/* Main Stats Cards */}
      <MetricsCard stats={stats} onResetDemo={handleResetDemo} />

      {/* Main Chart View wrapped in ErrorBoundary */}
      <ErrorBoundary>
        <ChartView
          candles={candles}
          activePosition={stats?.active_position}
          currentPrice={stats?.current_price}
          symbol={stats?.symbol}
        />
      </ErrorBoundary>

      {/* Grid: Trade History & Realtime Console Logs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '24px' }}>
        <div style={{ flex: 1 }}>
          <TradeHistory trades={stats?.trade_history} />
        </div>

        {/* Realtime Terminal Console Logs */}
        <div className="glass-panel" style={{ padding: '20px', height: 'fit-content' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Terminal size={20} color="#00f2fe" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              LIVE SYSTEM LOGS
            </h3>
          </div>

          <div 
            ref={logsContainerRef}
            style={{
              background: 'rgba(0, 0, 0, 0.5)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: '10px',
              padding: '12px',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.78rem',
              height: '240px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            {stats?.logs && stats.logs.length > 0 ? (
              stats.logs.map((log, index) => (
                <div key={index} style={{
                  color: log.includes('BUY') ? '#00e676' : (log.includes('CLOSED') ? '#ffc107' : (log.includes('⚠️') ? '#ff1744' : 'var(--text-secondary)'))
                }}>
                  {log}
                </div>
              ))
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>
                {stats ? 'Mencari sinyal indikator & log sistem...' : 'Menghubungkan ke Backend Engine...'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {isSettingsOpen && (
        <SettingsModal
          config={stats?.config}
          onClose={() => setIsSettingsOpen(false)}
          onSave={handleSaveSettings}
          API_BASE={API_BASE}
        />
      )}
    </div>
  );
}
