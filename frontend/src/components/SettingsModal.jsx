import React, { useState, useEffect } from 'react';
import { X, Send, Sliders, Key, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function SettingsModal({ config, onClose, onSave, API_BASE }) {
  const [tab, setTab] = useState('STRATEGY'); // STRATEGY, TELEGRAM, EXCHANGE
  const [isCustomSymbol, setIsCustomSymbol] = useState(false);
  const [formData, setFormData] = useState({
    symbol: config?.symbol || 'BTC/USDT',
    timeframe: config?.timeframe || '15m',
    ema_fast: config?.ema_fast ?? 9,
    ema_slow: config?.ema_slow ?? 21,
    rsi_period: config?.rsi_period ?? 14,
    rsi_oversold: config?.rsi_oversold ?? 35.0,
    rsi_overbought: config?.rsi_overbought ?? 65.0,
    stop_loss_pct: config?.stop_loss_pct ?? 1.5,
    take_profit_pct: config?.take_profit_pct ?? 3.0,
    risk_per_trade_pct: config?.risk_per_trade_pct ?? 1.0,
    max_daily_drawdown_pct: config?.max_daily_drawdown_pct ?? 3.0,
    telegram_bot_token: config?.telegram_bot_token || '',
    telegram_chat_id: config?.telegram_chat_id || '',
    exchange_id: config?.exchange_id || 'tokocrypto',
    exchange_api_key: config?.exchange_api_key || '',
    exchange_api_secret: config?.exchange_api_secret || ''
  });

  // Automatically update form fields when config prop changes / loads
  useEffect(() => {
    if (config) {
      setFormData(prev => ({
        ...prev,
        symbol: config.symbol || prev.symbol,
        timeframe: config.timeframe || prev.timeframe,
        ema_fast: config.ema_fast ?? prev.ema_fast,
        ema_slow: config.ema_slow ?? prev.ema_slow,
        rsi_period: config.rsi_period ?? prev.rsi_period,
        rsi_oversold: config.rsi_oversold ?? prev.rsi_oversold,
        rsi_overbought: config.rsi_overbought ?? prev.rsi_overbought,
        stop_loss_pct: config.stop_loss_pct ?? prev.stop_loss_pct,
        take_profit_pct: config.take_profit_pct ?? prev.take_profit_pct,
        risk_per_trade_pct: config.risk_per_trade_pct ?? prev.risk_per_trade_pct,
        max_daily_drawdown_pct: config.max_daily_drawdown_pct ?? prev.max_daily_drawdown_pct,
        telegram_bot_token: config.telegram_bot_token || prev.telegram_bot_token,
        telegram_chat_id: config.telegram_chat_id || prev.telegram_chat_id,
        exchange_id: config.exchange_id || prev.exchange_id,
        exchange_api_key: config.exchange_api_key || prev.exchange_api_key,
        exchange_api_secret: config.exchange_api_secret || prev.exchange_api_secret
      }));
    }
  }, [config]);

  const [testStatus, setTestStatus] = useState(null);
  const [isTesting, setIsTesting] = useState(false);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    let parsedValue = value;
    if (type === 'number') {
      parsedValue = value === '' ? '' : parseFloat(value);
    }
    setFormData(prev => ({
      ...prev,
      [name]: parsedValue
    }));
  };

  const handleTestTelegram = async () => {
    setIsTesting(true);
    setTestStatus(null);
    try {
      await axios.post(`${API_BASE}/api/settings/update`, formData);
      const res = await axios.post(`${API_BASE}/api/telegram/test`);
      setTestStatus({ type: 'success', message: res.data.message });
    } catch (err) {
      setTestStatus({ type: 'error', message: err.response?.data?.detail || 'Gagal mengirim pesan Telegram' });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  const popularSymbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT'];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '640px', maxHeight: '90vh', overflowY: 'auto', padding: '24px', position: 'relative' }}>
        {/* Close Button */}
        <button onClick={onClose} style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <X size={20} />
        </button>

        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '20px', background: 'linear-gradient(90deg, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          PENGATURAN BOT & INTEGRASI
        </h2>

        {/* Tab Selector */}
        <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--bg-card-border)', marginBottom: '20px', paddingBottom: '8px' }}>
          <button
            type="button"
            onClick={() => setTab('STRATEGY')}
            style={{
              background: 'none',
              border: 'none',
              color: tab === 'STRATEGY' ? '#00f2fe' : 'var(--text-muted)',
              borderBottom: tab === 'STRATEGY' ? '2px solid #00f2fe' : 'none',
              padding: '6px 12px',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Sliders size={16} /> Parameter Strategi
          </button>
          <button
            type="button"
            onClick={() => setTab('TELEGRAM')}
            style={{
              background: 'none',
              border: 'none',
              color: tab === 'TELEGRAM' ? '#00f2fe' : 'var(--text-muted)',
              borderBottom: tab === 'TELEGRAM' ? '2px solid #00f2fe' : 'none',
              padding: '6px 12px',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Send size={16} /> Telegram Bot
          </button>
          <button
            type="button"
            onClick={() => setTab('EXCHANGE')}
            style={{
              background: 'none',
              border: 'none',
              color: tab === 'EXCHANGE' ? '#00f2fe' : 'var(--text-muted)',
              borderBottom: tab === 'EXCHANGE' ? '2px solid #00f2fe' : 'none',
              padding: '6px 12px',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Key size={16} /> Live Exchange API
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* TAB 1: STRATEGY */}
          {tab === 'STRATEGY' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Trading Symbol</label>
                {!isCustomSymbol ? (
                  <select 
                    name="symbol" 
                    value={formData.symbol} 
                    onChange={(e) => {
                      if (e.target.value === 'CUSTOM') {
                        setIsCustomSymbol(true);
                      } else {
                        handleChange(e);
                      }
                    }} 
                    style={{ width: '100%' }}
                  >
                    {popularSymbols.map(sym => (
                      <option key={sym} value={sym}>{sym}</option>
                    ))}
                    <option value="CUSTOM">✏️ Custom Pair...</option>
                  </select>
                ) : (
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <input 
                      name="symbol" 
                      value={formData.symbol} 
                      onChange={handleChange} 
                      placeholder="e.g. PEPE/USDT" 
                      style={{ width: '100%' }} 
                    />
                    <button 
                      type="button" 
                      onClick={() => setIsCustomSymbol(false)} 
                      style={{ background: 'rgba(255, 255, 255, 0.08)', border: '1px solid var(--bg-card-border)', color: '#fff', padding: '0 10px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.75rem' }}
                    >
                      Batal
                    </button>
                  </div>
                )}
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Timeframe Candle</label>
                <select name="timeframe" value={formData.timeframe} onChange={handleChange} style={{ width: '100%' }}>
                  <option value="1m">1 Menit (1m)</option>
                  <option value="5m">5 Menit (5m)</option>
                  <option value="15m">15 Menit (15m)</option>
                  <option value="1h">1 Jam (1h)</option>
                  <option value="4h">4 Jam (4h)</option>
                  <option value="1d">1 Hari (1d)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>EMA Fast Period</label>
                <input type="number" name="ema_fast" value={formData.ema_fast} onChange={handleChange} style={{ width: '100%' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>EMA Slow Period</label>
                <input type="number" name="ema_slow" value={formData.ema_slow} onChange={handleChange} style={{ width: '100%' }} />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>RSI Period</label>
                <input type="number" name="rsi_period" value={formData.rsi_period} onChange={handleChange} style={{ width: '100%' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>RSI Oversold / Overbought</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input type="number" name="rsi_oversold" value={formData.rsi_oversold} onChange={handleChange} placeholder="35" style={{ width: '50%' }} />
                  <input type="number" name="rsi_overbought" value={formData.rsi_overbought} onChange={handleChange} placeholder="65" style={{ width: '50%' }} />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Stop Loss (% Price)</label>
                <input type="number" step="0.1" name="stop_loss_pct" value={formData.stop_loss_pct} onChange={handleChange} style={{ width: '100%' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Take Profit (% Price)</label>
                <input type="number" step="0.1" name="take_profit_pct" value={formData.take_profit_pct} onChange={handleChange} style={{ width: '100%' }} />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Risk Per Trade (% Saldo)</label>
                <input type="number" step="0.1" name="risk_per_trade_pct" value={formData.risk_per_trade_pct} onChange={handleChange} style={{ width: '100%' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Max Daily Drawdown Limit (%)</label>
                <input type="number" step="0.5" name="max_daily_drawdown_pct" value={formData.max_daily_drawdown_pct} onChange={handleChange} style={{ width: '100%' }} />
              </div>
            </div>
          )}

          {/* TAB 2: TELEGRAM */}
          {tab === 'TELEGRAM' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Telegram Bot Token</label>
                <input name="telegram_bot_token" value={formData.telegram_bot_token} onChange={handleChange} placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ" style={{ width: '100%' }} />
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>Dapatkan token gratis dari @BotFather di Telegram</span>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Telegram Chat ID</label>
                <input name="telegram_chat_id" value={formData.telegram_chat_id} onChange={handleChange} placeholder="987654321" style={{ width: '100%' }} />
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>Dapatkan Chat ID Anda dari @userinfobot di Telegram</span>
              </div>

              <button
                type="button"
                onClick={handleTestTelegram}
                disabled={isTesting}
                className="btn btn-secondary"
                style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}
              >
                <Send size={16} /> {isTesting ? 'Mengirim Tes Pesan...' : 'Test Send Telegram Notification'}
              </button>

              {testStatus && (
                <div style={{
                  padding: '10px 14px',
                  borderRadius: '8px',
                  fontSize: '0.82rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: testStatus.type === 'success' ? 'rgba(0, 230, 118, 0.12)' : 'rgba(255, 23, 68, 0.12)',
                  color: testStatus.type === 'success' ? '#00e676' : '#ff1744',
                  border: `1px solid ${testStatus.type === 'success' ? 'rgba(0, 230, 118, 0.3)' : 'rgba(255, 23, 68, 0.3)'}`
                }}>
                  {testStatus.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                  <span>{testStatus.message}</span>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: LIVE EXCHANGE API */}
          {tab === 'EXCHANGE' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ background: 'rgba(0, 242, 254, 0.08)', border: '1px solid rgba(0, 242, 254, 0.25)', padding: '12px', borderRadius: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '10px' }}>
                <ShieldCheck size={24} color="#00f2fe" style={{ flexShrink: 0 }} />
                <div>
                  <strong style={{ color: '#fff' }}>Panduan Keamanan API Key:</strong>
                  <p style={{ marginTop: '4px' }}>Disarankan memilih centang <b>Trading Only</b> pada bursa Anda. <b>JANGAN CENTANG (UNCHECK) IZIN WITHDRAWAL</b> demi keamanan dana Anda.</p>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Pilih Bursa Kripto</label>
                <select name="exchange_id" value={formData.exchange_id} onChange={handleChange} style={{ width: '100%' }}>
                  <option value="tokocrypto">Tokocrypto (Indonesia)</option>
                  <option value="binance">Binance (International)</option>
                  <option value="bybit">Bybit</option>
                  <option value="kucoin">KuCoin</option>
                  <option value="okx">OKX</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Exchange API Key</label>
                <input name="exchange_api_key" value={formData.exchange_api_key} onChange={handleChange} placeholder="Masukkan API Key" style={{ width: '100%' }} />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Exchange API Secret</label>
                <input type="password" name="exchange_api_secret" value={formData.exchange_api_secret} onChange={handleChange} placeholder="Masukkan API Secret" style={{ width: '100%' }} />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px', borderTop: '1px solid var(--bg-card-border)', paddingTop: '16px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Batal</button>
            <button type="submit" className="btn btn-primary">Simpan Pengaturan</button>
          </div>
        </form>
      </div>
    </div>
  );
}
