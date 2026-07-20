import React, { useEffect, useRef } from 'react';
import { createChart, CandlestickSeries, ColorType, createSeriesMarkers } from 'lightweight-charts';
import { TrendingUp } from 'lucide-react';

export default function ChartView({ candles, activePosition, symbol }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const markersRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initialize Lightweight Chart with Local Timezone (WIB) Formatting
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
        fontFamily: 'Outfit, sans-serif'
      },
      localization: {
        timeFormatter: (time) => {
          const date = new Date(time * 1000);
          const hours = date.getHours().toString().padStart(2, '0');
          const minutes = date.getMinutes().toString().padStart(2, '0');
          return `${hours}:${minutes} WIB`;
        }
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.04)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.04)' }
      },
      width: chartContainerRef.current.clientWidth,
      height: 380,
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.08)',
        timeVisible: true,
        secondsVisible: false,
        tickMarkFormatter: (time) => {
          const date = new Date(time * 1000);
          const hours = date.getHours().toString().padStart(2, '0');
          const minutes = date.getMinutes().toString().padStart(2, '0');
          return `${hours}:${minutes}`;
        }
      },
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.08)'
      }
    });

    // Support Lightweight Charts v5 (addSeries) & v4 (addCandlestickSeries)
    let candlestickSeries;
    const seriesOptions = {
      upColor: '#00e676',
      downColor: '#ff1744',
      borderVisible: false,
      wickUpColor: '#00e676',
      wickDownColor: '#ff1744'
    };

    if (typeof chart.addSeries === 'function' && CandlestickSeries) {
      candlestickSeries = chart.addSeries(CandlestickSeries, seriesOptions);
    } else if (typeof chart.addCandlestickSeries === 'function') {
      candlestickSeries = chart.addCandlestickSeries(seriesOptions);
    }

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (markersRef.current && typeof markersRef.current.detach === 'function') {
        try { markersRef.current.detach(); } catch (e) {}
      }
      chart.remove();
    };
  }, []);

  // Update Candles & Markers
  useEffect(() => {
    if (!candlestickSeriesRef.current || !candles || candles.length === 0) return;

    // Filter duplicate timestamps
    const uniqueCandles = [];
    const seenTimes = new Set();
    candles.forEach(c => {
      if (!seenTimes.has(c.time)) {
        seenTimes.add(c.time);
        uniqueCandles.push(c);
      }
    });

    uniqueCandles.sort((a, b) => a.time - b.time);
    candlestickSeriesRef.current.setData(uniqueCandles);

    // Prepare markers
    const newMarkers = [];
    if (activePosition) {
      const lastCandleTime = uniqueCandles[uniqueCandles.length - 1]?.time;
      if (lastCandleTime) {
        newMarkers.push({
          time: lastCandleTime,
          position: activePosition.side === 'BUY' ? 'belowBar' : 'aboveBar',
          color: activePosition.side === 'BUY' ? '#00e676' : '#ff1744',
          shape: activePosition.side === 'BUY' ? 'arrowUp' : 'arrowDown',
          text: `${activePosition.side} @ $${activePosition.entry_price.toLocaleString()}`
        });
      }
    }

    // Apply markers safely for v4 & v5
    try {
      if (markersRef.current && typeof markersRef.current.setMarkers === 'function') {
        markersRef.current.setMarkers(newMarkers);
      } else if (typeof createSeriesMarkers === 'function') {
        markersRef.current = createSeriesMarkers(candlestickSeriesRef.current, newMarkers);
      } else if (typeof candlestickSeriesRef.current.setMarkers === 'function') {
        candlestickSeriesRef.current.setMarkers(newMarkers);
      }
    } catch (e) {
      console.warn('Marker set warning:', e);
    }
  }, [candles, activePosition]);

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={20} color="#00f2fe" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            LIVE CANDLESTICK CHART ({symbol || 'BTC/USDT'})
          </h3>
        </div>
        
        {activePosition && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.82rem', background: 'rgba(0, 230, 118, 0.1)', border: '1px solid rgba(0, 230, 118, 0.3)', color: '#00e676', padding: '4px 12px', borderRadius: '12px' }}>
            <span>POSISI AKTIF: <b>{activePosition.side}</b> @ ${activePosition.entry_price.toLocaleString()}</span>
            <span>SL: ${activePosition.sl_price.toLocaleString()}</span>
            <span>TP: ${activePosition.tp_price.toLocaleString()}</span>
          </div>
        )}
      </div>

      <div ref={chartContainerRef} style={{ width: '100%', height: '380px' }} />
    </div>
  );
}
