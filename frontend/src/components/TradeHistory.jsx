import React, { useState } from 'react';
import { History, ArrowUpRight, ArrowDownRight, Tag } from 'lucide-react';

export default function TradeHistory({ trades }) {
  const [filter, setFilter] = useState('ALL'); // ALL, WIN, LOSS

  const filteredTrades = (trades || []).filter(trade => {
    if (filter === 'WIN') return trade.pnl > 0;
    if (filter === 'LOSS') return trade.pnl < 0;
    return true;
  });

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <History size={20} color="#00f2fe" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            RIWAYAT TRANSAKSI BOT
          </h3>
        </div>

        {/* Filter Buttons */}
        <div style={{ display: 'flex', gap: '6px' }}>
          {['ALL', 'WIN', 'LOSS'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                background: filter === f ? 'rgba(0, 242, 254, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                border: `1px solid ${filter === f ? 'rgba(0, 242, 254, 0.4)' : 'var(--bg-card-border)'}`,
                color: filter === f ? '#00f2fe' : 'var(--text-muted)',
                padding: '4px 12px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {filteredTrades.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Belum ada riwayat transaksi. Bot akan mencatat otomatis begitu order tertutup.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem', textWrap: 'nowrap' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--bg-card-border)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                <th style={{ padding: '10px 12px' }}>ID & PAIR</th>
                <th style={{ padding: '10px 12px' }}>TIPE</th>
                <th style={{ padding: '10px 12px' }}>ENTRY PRICE</th>
                <th style={{ padding: '10px 12px' }}>EXIT PRICE</th>
                <th style={{ padding: '10px 12px' }}>AMOUNT</th>
                <th style={{ padding: '10px 12px' }}>PROFIT / LOSS</th>
                <th style={{ padding: '10px 12px' }}>REASON</th>
              </tr>
            </thead>
            <tbody>
              {filteredTrades.map(trade => {
                const isProfit = trade.pnl >= 0;
                return (
                  <tr key={trade.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', transition: 'background 0.2s' }}>
                    <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      <div style={{ color: '#fff' }}>{trade.symbol}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{trade.id} ({trade.mode})</div>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        background: trade.side === 'BUY' ? 'rgba(0, 230, 118, 0.12)' : 'rgba(255, 23, 68, 0.12)',
                        color: trade.side === 'BUY' ? '#00e676' : '#ff1744',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        {trade.side === 'BUY' ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                        {trade.side}
                      </span>
                    </td>
                    <td style={{ padding: '12px', fontFamily: 'var(--font-mono)' }}>${trade.entry_price.toLocaleString()}</td>
                    <td style={{ padding: '12px', fontFamily: 'var(--font-mono)' }}>${trade.exit_price.toLocaleString()}</td>
                    <td style={{ padding: '12px', fontFamily: 'var(--font-mono)' }}>{trade.amount}</td>
                    <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: isProfit ? '#00e676' : '#ff1744' }}>
                      {isProfit ? '+' : ''}${trade.pnl.toFixed(2)} ({isProfit ? '+' : ''}{trade.pnl_pct.toFixed(2)}%)
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        fontSize: '0.75rem', 
                        color: 'var(--text-secondary)',
                        background: 'rgba(255, 255, 255, 0.05)',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        border: '1px solid var(--bg-card-border)'
                      }}>
                        {trade.close_reason}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
