import React from 'react';
import { Play, Square, Settings, Send, ShieldAlert, Cpu } from 'lucide-react';

export default function Header({ stats, onStart, onStop, onOpenSettings, onToggleMode }) {
  const isRunning = stats?.is_running || false;
  const mode = stats?.trading_mode || 'demo';
  const isDemo = mode === 'demo';
  const telegramActive = stats?.telegram_configured || false;

  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
      {/* Left: Brand & Symbol info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ background: 'linear-gradient(135deg, #00f2fe, #4facfe)', padding: '10px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Cpu size={24} color="#000" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.35rem', fontWeight: 700, letterSpacing: '-0.5px', background: 'linear-gradient(90deg, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            QUANTBOT PRO <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '6px', background: 'rgba(0, 242, 254, 0.15)', color: '#00f2fe', WebkitTextFillColor: 'initial', verticalAlign: 'middle', border: '1px solid rgba(0, 242, 254, 0.3)' }}>v1.0</span>
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#f8fafc' }}>{stats?.symbol || 'BTC/USDT'}</span>
            <span>•</span>
            <span>TF: {stats?.timeframe || '1m'}</span>
            <span>•</span>
            <span style={{ color: '#00f2fe' }}>${stats?.current_price ? stats.current_price.toLocaleString() : '0.00'}</span>
          </div>
        </div>
      </div>

      {/* Center: Badges (Mode & Telegram) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {/* Mode Switcher Toggle */}
        <button 
          onClick={onToggleMode}
          title="Klik untuk mengganti mode (Demo / Live)"
          style={{
            background: isDemo ? 'rgba(255, 193, 7, 0.12)' : 'rgba(255, 23, 68, 0.15)',
            border: `1px solid ${isDemo ? 'rgba(255, 193, 7, 0.4)' : 'rgba(255, 23, 68, 0.4)'}`,
            color: isDemo ? 'var(--accent-yellow)' : 'var(--accent-red)',
            padding: '6px 14px',
            borderRadius: '20px',
            fontWeight: 700,
            fontSize: '0.82rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease'
          }}
        >
          {isDemo ? (
            <>🟡 DEMO (PAPER TRADING)</>
          ) : (
            <>🔴 LIVE TRADING ACTIVE</>
          )}
        </button>

        {/* Telegram Status Badge */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '6px', 
          padding: '6px 12px', 
          borderRadius: '20px', 
          fontSize: '0.8rem', 
          background: telegramActive ? 'rgba(0, 242, 254, 0.1)' : 'rgba(255, 255, 255, 0.05)',
          color: telegramActive ? '#00f2fe' : 'var(--text-muted)',
          border: `1px solid ${telegramActive ? 'rgba(0, 242, 254, 0.3)' : 'var(--bg-card-border)'}`
        }}>
          <Send size={14} />
          <span>{telegramActive ? 'Telegram Connected' : 'Telegram Off'}</span>
        </div>

        {/* Bot Running Status */}
        <div className={`pulse-badge ${isRunning ? 'active' : 'paused'}`}>
          <div className="dot" />
          <span>{isRunning ? 'BOT ACTIVE' : 'BOT PAUSED'}</span>
        </div>
      </div>

      {/* Right: Actions (Start/Stop & Settings) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {!isRunning ? (
          <button className="btn btn-primary" onClick={onStart}>
            <Play size={16} fill="#000" />
            <span>START BOT</span>
          </button>
        ) : (
          <button className="btn btn-danger" onClick={onStop}>
            <Square size={16} fill="#fff" />
            <span>STOP BOT</span>
          </button>
        )}

        <button className="btn btn-secondary" onClick={onOpenSettings} title="Buka Pengaturan">
          <Settings size={18} />
          <span>SETTINGS</span>
        </button>
      </div>
    </header>
  );
}
