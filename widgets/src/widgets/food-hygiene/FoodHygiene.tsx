import React from 'react'
import type { FoodHygieneData, Establishment } from './main'

interface FoodHygieneProps {
  data: FoodHygieneData
}

const RatingBadge: React.FC<{ rating: string }> = ({ rating }) => {
  const ratingNum = parseInt(rating, 10)

  const getRatingStyle = () => {
    if (rating === 'Pass' || ratingNum >= 4) {
      return { bg: '#cce2d8', color: '#005a30', label: rating === 'Pass' ? 'Pass' : rating }
    }
    if (ratingNum === 3) {
      return { bg: '#fff2cc', color: '#594d00', label: '3' }
    }
    if (ratingNum >= 1) {
      return { bg: '#fcd6c3', color: '#6e3619', label: rating }
    }
    return { bg: '#f6d7d2', color: '#942514', label: rating === '0' ? '0' : rating }
  }

  const { bg, color, label } = getRatingStyle()

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '4px',
      background: bg,
      color,
      padding: '6px 12px',
      borderRadius: '4px',
      fontWeight: 600,
      fontSize: '16px',
      minWidth: '40px',
      justifyContent: 'center'
    }}>
      {!isNaN(ratingNum) && <span style={{ fontSize: '12px' }}>★</span>}
      {label}
    </div>
  )
}

const EstablishmentCard: React.FC<{ establishment: Establishment }> = ({ establishment }) => {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  return (
    <div className="status-card" style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
      <RatingBadge rating={establishment.rating} />
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, marginBottom: '4px' }}>{establishment.name}</div>
        <div style={{ fontSize: '13px', color: '#505a5f', marginBottom: '4px' }}>
          {establishment.address}
        </div>
        <div style={{ fontSize: '12px', color: '#505a5f', display: 'flex', gap: '12px' }}>
          {establishment.business_type && <span>{establishment.business_type}</span>}
          <span>Inspected: {formatDate(establishment.inspection_date)}</span>
        </div>
      </div>
    </div>
  )
}

const FoodHygiene: React.FC<FoodHygieneProps> = ({ data }) => {
  const getRatingSummary = () => {
    const ratings = data.establishments.map(e => parseInt(e.rating, 10)).filter(r => !isNaN(r))
    if (ratings.length === 0) return null

    const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length
    const high = ratings.filter(r => r >= 4).length
    const low = ratings.filter(r => r <= 2).length

    return { avg: avg.toFixed(1), high, low }
  }

  const summary = getRatingSummary()

  return (
    <div className="widget-container">
      <h1 className="widget-title">Food Hygiene Ratings</h1>
      {data.postcode && (
        <p className="widget-subtitle">
          {data.total_results} establishments near {data.postcode}
        </p>
      )}
      {data.query && (
        <p className="widget-subtitle">
          {data.total_results} results for "{data.query}"
        </p>
      )}

      {/* Rating Summary */}
      {summary && (
        <div className="grid grid-3" style={{ marginBottom: '16px' }}>
          <div className="info-card">
            <div className="info-label">Avg Rating</div>
            <div className="info-value">{summary.avg}</div>
          </div>
          <div className="info-card">
            <div className="info-label">Rating 4-5</div>
            <div className="info-value" style={{ color: '#005a30' }}>{summary.high}</div>
          </div>
          <div className="info-card">
            <div className="info-label">Rating 0-2</div>
            <div className="info-value" style={{ color: summary.low > 0 ? '#942514' : '#505a5f' }}>
              {summary.low}
            </div>
          </div>
        </div>
      )}

      {/* Rating Scale */}
      <div style={{
        display: 'flex',
        gap: '4px',
        marginBottom: '16px',
        fontSize: '11px',
        color: '#505a5f'
      }}>
        <span style={{ background: '#cce2d8', padding: '2px 6px', borderRadius: '2px' }}>5 Very Good</span>
        <span style={{ background: '#d4e4f7', padding: '2px 6px', borderRadius: '2px' }}>4 Good</span>
        <span style={{ background: '#fff2cc', padding: '2px 6px', borderRadius: '2px' }}>3 Satisfactory</span>
        <span style={{ background: '#fcd6c3', padding: '2px 6px', borderRadius: '2px' }}>2 Needs Improvement</span>
      </div>

      {/* Establishments */}
      {data.establishments.map((establishment, index) => (
        <EstablishmentCard key={index} establishment={establishment} />
      ))}

      <div className="widget-footer">
        Data from {data.data_source} | Showing {data.showing} of {data.total_results}
      </div>
    </div>
  )
}

export default FoodHygiene
