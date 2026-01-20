import React from 'react'
import type { TubeStatusData, TubeLine } from './main'

interface TubeStatusProps {
  data: TubeStatusData
}

// Tube line colors
const lineColors: Record<string, string> = {
  'Bakerloo': '#B36305',
  'Central': '#E32017',
  'Circle': '#FFD300',
  'District': '#00782A',
  'Hammersmith & City': '#F3A9BB',
  'Jubilee': '#A0A5A9',
  'Metropolitan': '#9B0056',
  'Northern': '#000000',
  'Piccadilly': '#003688',
  'Victoria': '#0098D4',
  'Waterloo & City': '#95CDBA',
  'Elizabeth': '#6950a1',
  'DLR': '#00A4A7',
  'Overground': '#EE7C0E',
  'TfL Rail': '#0019A8'
}

const getStatusType = (status: string): 'good' | 'warning' | 'error' => {
  const lowerStatus = status.toLowerCase()
  if (lowerStatus.includes('good service') || lowerStatus.includes('special service')) {
    return 'good'
  }
  if (lowerStatus.includes('minor') || lowerStatus.includes('reduced')) {
    return 'warning'
  }
  return 'error'
}

const LineCard: React.FC<{ line: TubeLine }> = ({ line }) => {
  const statusType = getStatusType(line.status)
  const color = lineColors[line.name] || '#666666'

  return (
    <div className={`status-card ${statusType}`} style={{ borderLeftColor: color }}>
      <div className="status-card-header">
        <span className="status-card-title">{line.name}</span>
        <span className={`status-badge ${statusType}`}>{line.status}</span>
      </div>
      {line.reason && (
        <div className="status-card-detail">{line.reason}</div>
      )}
    </div>
  )
}

const TubeStatus: React.FC<TubeStatusProps> = ({ data }) => {
  const goodLines = data.lines.filter(l => getStatusType(l.status) === 'good')
  const problemLines = data.lines.filter(l => getStatusType(l.status) !== 'good')

  return (
    <div className="widget-container">
      <h1 className="widget-title">London Underground Status</h1>

      {problemLines.length > 0 && (
        <>
          <h2 className="widget-subtitle">
            {problemLines.length} line{problemLines.length !== 1 ? 's' : ''} with issues
          </h2>
          {problemLines.map(line => (
            <LineCard key={line.name} line={line} />
          ))}
        </>
      )}

      {goodLines.length > 0 && (
        <>
          <h2 className="widget-subtitle" style={{ marginTop: problemLines.length > 0 ? '16px' : '0' }}>
            {goodLines.length} line{goodLines.length !== 1 ? 's' : ''} running normally
          </h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {goodLines.map(line => (
              <div
                key={line.name}
                style={{
                  background: lineColors[line.name] || '#666',
                  color: ['Circle', 'Hammersmith & City', 'Waterloo & City'].includes(line.name) ? '#000' : '#fff',
                  padding: '4px 12px',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontWeight: 500
                }}
              >
                {line.name}
              </div>
            ))}
          </div>
        </>
      )}

      <div className="widget-footer">
        Data from {data.data_source} | Updated {new Date(data.retrieved_at).toLocaleTimeString()}
      </div>
    </div>
  )
}

export default TubeStatus
