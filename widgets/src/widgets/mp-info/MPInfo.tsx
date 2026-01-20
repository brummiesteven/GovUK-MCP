import React from 'react'
import type { MPData } from './main'

interface MPInfoProps {
  data: MPData
}

const partyColors: Record<string, { bg: string; text: string }> = {
  'Labour': { bg: '#E4003B', text: 'white' },
  'Conservative': { bg: '#0087DC', text: 'white' },
  'Liberal Democrat': { bg: '#FAA61A', text: 'black' },
  'Scottish National Party': { bg: '#FDF38E', text: 'black' },
  'Green Party': { bg: '#6AB023', text: 'white' },
  'Plaid Cymru': { bg: '#005B54', text: 'white' },
  'Democratic Unionist Party': { bg: '#D46A4C', text: 'white' },
  'Sinn Féin': { bg: '#326760', text: 'white' },
  'Alba Party': { bg: '#005EB8', text: 'white' },
  'Reform UK': { bg: '#12B6CF', text: 'white' },
  'Independent': { bg: '#DDDDDD', text: 'black' }
}

const MPInfo: React.FC<MPInfoProps> = ({ data }) => {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  const getYearsServed = () => {
    if (!data.membership_start) return null
    const start = new Date(data.membership_start)
    const now = new Date()
    const years = Math.floor((now.getTime() - start.getTime()) / (365.25 * 24 * 60 * 60 * 1000))
    return years
  }

  const partyStyle = partyColors[data.party] || { bg: '#666', text: 'white' }
  const yearsServed = getYearsServed()

  return (
    <div className="widget-container">
      {/* Header with photo */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
        {data.thumbnail_url && (
          <div style={{
            width: '80px',
            height: '100px',
            borderRadius: '4px',
            overflow: 'hidden',
            flexShrink: 0,
            background: '#f3f2f1'
          }}>
            <img
              src={data.thumbnail_url}
              alt={data.name}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none'
              }}
            />
          </div>
        )}
        <div>
          <h1 className="widget-title" style={{ marginBottom: '8px' }}>{data.name}</h1>
          <div style={{
            display: 'inline-block',
            background: partyStyle.bg,
            color: partyStyle.text,
            padding: '4px 12px',
            borderRadius: '4px',
            fontWeight: 600,
            fontSize: '14px',
            marginBottom: '8px'
          }}>
            {data.party}
          </div>
          <div style={{ fontSize: '14px', color: '#505a5f' }}>
            MP for {data.constituency}
          </div>
        </div>
      </div>

      {/* Details */}
      <div className="grid grid-2" style={{ marginBottom: '16px' }}>
        {data.membership_start && (
          <div className="info-card">
            <div className="info-label">MP Since</div>
            <div className="info-value" style={{ fontSize: '14px' }}>
              {formatDate(data.membership_start)}
            </div>
          </div>
        )}
        {yearsServed !== null && (
          <div className="info-card">
            <div className="info-label">Years Served</div>
            <div className="info-value">{yearsServed}</div>
          </div>
        )}
      </div>

      <div className="info-card" style={{ marginBottom: '16px' }}>
        <div className="info-label">Constituency</div>
        <div className="info-value" style={{ fontSize: '14px' }}>{data.constituency}</div>
      </div>

      {/* Parliament ID */}
      <div style={{
        fontSize: '12px',
        color: '#505a5f',
        padding: '8px',
        background: '#f3f2f1',
        borderRadius: '4px',
        marginBottom: '16px'
      }}>
        Parliament Member ID: {data.id}
      </div>

      <div className="widget-footer">
        Data from {data.data_source}
      </div>
    </div>
  )
}

export default MPInfo
