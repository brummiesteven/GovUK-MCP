import React from 'react'
import type { PostcodeData } from './main'

interface PostcodeLookupProps {
  data: PostcodeData
}

const PostcodeLookup: React.FC<PostcodeLookupProps> = ({ data }) => {
  const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${data.longitude - 0.01},${data.latitude - 0.005},${data.longitude + 0.01},${data.latitude + 0.005}&layer=mapnik&marker=${data.latitude},${data.longitude}`

  return (
    <div className="widget-container">
      <h1 className="widget-title">{data.postcode}</h1>

      {/* Map */}
      <div style={{ marginBottom: '16px', borderRadius: '4px', overflow: 'hidden', border: '1px solid #b1b4b6' }}>
        <iframe
          width="100%"
          height="200"
          frameBorder="0"
          scrolling="no"
          src={mapUrl}
          style={{ display: 'block' }}
        />
      </div>

      {/* Location Info */}
      <div className="grid grid-2" style={{ marginBottom: '16px' }}>
        <div className="info-card">
          <div className="info-label">District</div>
          <div className="info-value">{data.admin_district}</div>
        </div>
        <div className="info-card">
          <div className="info-label">Region</div>
          <div className="info-value">{data.region}</div>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginBottom: '16px' }}>
        <div className="info-card">
          <div className="info-label">Country</div>
          <div className="info-value">{data.country}</div>
        </div>
        {data.ward && (
          <div className="info-card">
            <div className="info-label">Ward</div>
            <div className="info-value">{data.ward}</div>
          </div>
        )}
      </div>

      {/* Constituency */}
      <div className="info-card" style={{ marginBottom: '16px' }}>
        <div className="info-label">Parliamentary Constituency</div>
        <div className="info-value">{data.parliamentary_constituency}</div>
      </div>

      {/* Coordinates */}
      <div className="info-card" style={{ marginBottom: '16px' }}>
        <div className="info-label">Coordinates</div>
        <div className="info-value" style={{ fontSize: '14px' }}>
          {data.latitude.toFixed(6)}, {data.longitude.toFixed(6)}
        </div>
      </div>

      <div className="widget-footer">
        Data from {data.data_source}
      </div>
    </div>
  )
}

export default PostcodeLookup
