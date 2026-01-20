import React from 'react'
import type { CompanyData } from './main'

interface CompanyInfoProps {
  data: CompanyData
}

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusMap: Record<string, { label: string; className: string }> = {
    active: { label: 'Active', className: 'good' },
    dissolved: { label: 'Dissolved', className: 'error' },
    liquidation: { label: 'In Liquidation', className: 'error' },
    'voluntary-arrangement': { label: 'Voluntary Arrangement', className: 'warning' }
  }

  const { label, className } = statusMap[status.toLowerCase()] || { label: status, className: 'warning' }

  return <span className={`status-badge ${className}`}>{label}</span>
}

const CompanyTypeBadge: React.FC<{ type: string }> = ({ type }) => {
  const typeMap: Record<string, string> = {
    ltd: 'Private Limited',
    plc: 'Public Limited (PLC)',
    llp: 'Limited Liability Partnership',
    'private-unlimited': 'Private Unlimited',
    'private-limited-guarant-nsc': 'Limited by Guarantee'
  }

  return (
    <span style={{
      background: '#f3f2f1',
      padding: '2px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      color: '#505a5f'
    }}>
      {typeMap[type.toLowerCase()] || type.toUpperCase()}
    </span>
  )
}

const CompanyInfo: React.FC<CompanyInfoProps> = ({ data }) => {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  const formatAddress = () => {
    const addr = data.registered_office_address
    const parts = [
      addr.address_line_1,
      addr.locality,
      addr.postal_code,
      addr.country
    ].filter(Boolean)
    return parts.join(', ')
  }

  return (
    <div className="widget-container">
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
          <StatusBadge status={data.company_status} />
          <CompanyTypeBadge type={data.company_type} />
        </div>
        <h1 className="widget-title" style={{ marginBottom: '4px' }}>{data.company_name}</h1>
        <div style={{ color: '#505a5f', fontSize: '14px' }}>Company No. {data.company_number}</div>
      </div>

      {/* Key Details */}
      <div className="grid grid-2" style={{ marginBottom: '16px' }}>
        <div className="info-card">
          <div className="info-label">Incorporated</div>
          <div className="info-value" style={{ fontSize: '14px' }}>{formatDate(data.date_of_creation)}</div>
        </div>
        {data.sic_codes && data.sic_codes.length > 0 && (
          <div className="info-card">
            <div className="info-label">SIC Code</div>
            <div className="info-value" style={{ fontSize: '14px' }}>{data.sic_codes.join(', ')}</div>
          </div>
        )}
      </div>

      {/* Address */}
      <div className="info-card" style={{ marginBottom: '16px' }}>
        <div className="info-label">Registered Office</div>
        <div className="info-value" style={{ fontSize: '14px' }}>{formatAddress()}</div>
      </div>

      {/* Filing Deadlines */}
      {(data.accounts || data.confirmation_statement) && (
        <div style={{ marginBottom: '16px' }}>
          <h2 className="widget-subtitle">Filing Deadlines</h2>
          <div className="grid grid-2">
            {data.accounts && (
              <div className={`status-card ${data.accounts.overdue ? 'error' : 'good'}`}>
                <div className="status-card-header">
                  <span className="status-card-title">Accounts</span>
                  {data.accounts.overdue && <span className="status-badge error">Overdue</span>}
                </div>
                <div className="status-card-detail">
                  Due: {data.accounts.next_due ? formatDate(data.accounts.next_due) : 'N/A'}
                </div>
              </div>
            )}
            {data.confirmation_statement && (
              <div className={`status-card ${data.confirmation_statement.overdue ? 'error' : 'good'}`}>
                <div className="status-card-header">
                  <span className="status-card-title">Confirmation</span>
                  {data.confirmation_statement.overdue && <span className="status-badge error">Overdue</span>}
                </div>
                <div className="status-card-detail">
                  Due: {data.confirmation_statement.next_due ? formatDate(data.confirmation_statement.next_due) : 'N/A'}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Flags */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
        {data.has_charges && (
          <span style={{ background: '#fff2cc', color: '#594d00', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
            Has Charges
          </span>
        )}
        {data.has_insolvency_history && (
          <span style={{ background: '#f6d7d2', color: '#942514', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
            Insolvency History
          </span>
        )}
        {!data.has_charges && !data.has_insolvency_history && (
          <span style={{ background: '#cce2d8', color: '#005a30', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
            No Charges or Insolvency
          </span>
        )}
      </div>

      <div className="widget-footer">
        Data from {data.data_source}
      </div>
    </div>
  )
}

export default CompanyInfo
