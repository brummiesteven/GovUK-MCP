import React from 'react'
import type { FloodWarningsData, FloodWarning } from './main'

interface FloodWarningsProps {
  data: FloodWarningsData
}

const SeverityIcon: React.FC<{ level: number }> = ({ level }) => {
  const icons: Record<number, { emoji: string; bg: string; color: string }> = {
    1: { emoji: '⚠️', bg: '#d4351c', color: 'white' },
    2: { emoji: '🌊', bg: '#f47738', color: 'white' },
    3: { emoji: '💧', bg: '#ffdd00', color: '#0b0c0c' },
    4: { emoji: '✓', bg: '#00703c', color: 'white' }
  }

  const { emoji, bg, color } = icons[level] || icons[3]

  return (
    <div style={{
      width: '36px',
      height: '36px',
      borderRadius: '50%',
      background: bg,
      color,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '18px',
      flexShrink: 0
    }}>
      {emoji}
    </div>
  )
}

const WarningCard: React.FC<{ warning: FloodWarning }> = ({ warning }) => {
  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr)
    return date.toLocaleString('en-GB', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getCardClass = () => {
    if (warning.severity_level === 1) return 'error'
    if (warning.severity_level === 2) return 'warning'
    return 'good'
  }

  return (
    <div className={`status-card ${getCardClass()}`} style={{ display: 'flex', gap: '12px' }}>
      <SeverityIcon level={warning.severity_level} />
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
          <span style={{ fontWeight: 600, color: warning.severity_level <= 2 ? '#d4351c' : '#0b0c0c' }}>
            {warning.severity}
          </span>
          <span style={{ fontSize: '12px', color: '#505a5f' }}>
            {formatTime(warning.time_raised)}
          </span>
        </div>
        <div style={{ fontWeight: 500, marginBottom: '4px' }}>{warning.area}</div>
        <div style={{ fontSize: '13px', color: '#505a5f' }}>{warning.description}</div>
        {warning.message && (
          <div style={{
            marginTop: '8px',
            padding: '8px',
            background: 'rgba(0,0,0,0.05)',
            borderRadius: '4px',
            fontSize: '13px'
          }}>
            {warning.message}
          </div>
        )}
      </div>
    </div>
  )
}

const FloodWarnings: React.FC<FloodWarningsProps> = ({ data }) => {
  const severe = data.warnings.filter(w => w.severity_level === 1).length
  const warnings = data.warnings.filter(w => w.severity_level === 2).length
  const alerts = data.warnings.filter(w => w.severity_level === 3).length

  return (
    <div className="widget-container">
      <h1 className="widget-title">Flood Warnings</h1>

      {data.total_warnings === 0 ? (
        <div className="status-card good" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>✓</div>
          <div style={{ fontWeight: 600, color: '#00703c' }}>No flood warnings in force</div>
        </div>
      ) : (
        <>
          {/* Summary */}
          <div className="grid grid-3" style={{ marginBottom: '16px' }}>
            <div className="info-card" style={{ borderLeft: severe > 0 ? '3px solid #d4351c' : undefined }}>
              <div className="info-label">Severe</div>
              <div className="info-value" style={{ color: severe > 0 ? '#d4351c' : '#505a5f' }}>
                {severe}
              </div>
            </div>
            <div className="info-card" style={{ borderLeft: warnings > 0 ? '3px solid #f47738' : undefined }}>
              <div className="info-label">Warnings</div>
              <div className="info-value" style={{ color: warnings > 0 ? '#f47738' : '#505a5f' }}>
                {warnings}
              </div>
            </div>
            <div className="info-card">
              <div className="info-label">Alerts</div>
              <div className="info-value">{alerts}</div>
            </div>
          </div>

          {/* Legend */}
          <div style={{
            display: 'flex',
            gap: '12px',
            marginBottom: '16px',
            fontSize: '12px',
            color: '#505a5f',
            flexWrap: 'wrap'
          }}>
            <span><span style={{ color: '#d4351c' }}>●</span> Severe: Danger to life</span>
            <span><span style={{ color: '#f47738' }}>●</span> Warning: Expect flooding</span>
            <span><span style={{ color: '#ffdd00' }}>●</span> Alert: Flooding possible</span>
          </div>

          {/* Warnings List */}
          {data.warnings.map((warning, index) => (
            <WarningCard key={index} warning={warning} />
          ))}
        </>
      )}

      <div className="widget-footer">
        Data from {data.data_source} | {data.total_warnings} active warning{data.total_warnings !== 1 ? 's' : ''}
      </div>
    </div>
  )
}

export default FloodWarnings
