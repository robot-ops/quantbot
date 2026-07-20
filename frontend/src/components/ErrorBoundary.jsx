import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary caught error]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="glass-panel" style={{ padding: '30px', textAlign: 'center', marginBottom: '24px' }}>
          <AlertCircle size={36} color="#ff1744" style={{ marginBottom: '12px' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>
            Komponen Grafik Memerlukan Refresh
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Terjadi kendala memuat visualisasi chart. Dashboard utama tetap berjalan normal.
          </p>
          <button
            className="btn btn-secondary"
            onClick={() => this.setState({ hasError: false })}
          >
            <RefreshCw size={16} /> Reload Chart Component
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
