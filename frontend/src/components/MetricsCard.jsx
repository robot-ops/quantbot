import React from 'react';
import { Wallet, DollarSign, Award, Activity, ShieldAlert, RotateCcw } from 'lucide-react';

export default function MetricsCard({ stats, onResetDemo }) {
  const balance = stats?.balance ?? 10000.0;
  const totalPnL = stats?.total_pnl ?? 0.0;
  const totalPnLPct = stats?.total_pnl_pct ?? 0.0;
  const winRate = stats?.win_rate ?? 0.0;
  const totalTrades = stats?.total_trades ?? 0;
  const isDemo = stats?.trading_mode === 'demo';

  const isProfitable = totalPnL >= 0;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
      {/* 1. Balance Card */}
      <div className="glass-panel" style={{ padding: '18px 20px', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            {isDemo ? 'SALDO PAPER TRADING' : 'SALDO LIVE TRADING'}
          </span>
          <Wallet size={20} color="#00f2fe" />
        </div>
        <div style={{ fontSize: '1.6rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
          ${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        
        {isDemo && (
          <button 
            onClick={onResetDemo} 
            title="Reset Saldo Demo ke $10,000" 
            style={{ 
              marginTop: '10px', 
              background: 'none', 
              border: 'none', 
              color: 'var(--text-muted)', 
              fontSize: '0.75rem', 
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <RotateCcw size={12} /> Reset Saldo Demo
          </button>
        )}
      </div>

      {/* 2. Total PnL Card */}
      <div className="glass-panel" style={{ padding: '18px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>TOTAL PROFIT / LOSS</span>
          <DollarSign size={20} color={isProfitable ? '#00e676' : '#ff1744'} />
        </div>
        <div style={{ fontSize: '1.6rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: isProfitable ? '#00e676' : '#ff1744' }}>
          {isProfitable ? '+' : ''}${totalPnL.toFixed(2)}
        </div>
        <div style={{ fontSize: '0.8rem', color: isProfitable ? '#00e676' : '#ff1744', marginTop: '4px', fontWeight: 600 }}>
          ({isProfitable ? '+' : ''}{totalPnLPct.toFixed(2)}%)
        </div>
      </div>

      {/* 3. Win Rate Card */}
      <div className="glass-panel" style={{ padding: '18px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>WIN RATE</span>
          <Award size={20} color="#ffc107" />
        </div>
        <div style={{ fontSize: '1.6rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#ffc107' }}>
          {winRate.toFixed(1)}%
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          {stats?.winning_trades || 0} Menang / {stats?.losing_trades || 0} Kalah
        </div>
      </div>

      {/* 4. Total Trades Card */}
      <div className="glass-panel" style={{ padding: '18px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>TOTAL TRANSAKSI</span>
          <Activity size={20} color="#7f00ff" />
        </div>
        <div style={{ fontSize: '1.6rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
          {totalTrades}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Trade Terbuka: {stats?.active_position ? '1 Posisi' : 'Tidak ada'}
        </div>
      </div>
    </div>
  );
}
