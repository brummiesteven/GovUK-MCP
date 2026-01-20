import React from 'react'
import ReactDOM from 'react-dom/client'
import CompanyInfo from './CompanyInfo'
import '@/components/styles.css'
import '@/types'

export interface CompanyData {
  company_number: string
  company_name: string
  company_status: string
  company_type: string
  date_of_creation: string
  registered_office_address: {
    address_line_1?: string
    locality?: string
    postal_code?: string
    country?: string
  }
  sic_codes?: string[]
  accounts?: {
    next_due?: string
    overdue?: boolean
  }
  confirmation_statement?: {
    next_due?: string
    overdue?: boolean
  }
  has_insolvency_history?: boolean
  has_charges?: boolean
  data_source: string
  retrieved_at: string
}

const getData = (): CompanyData => {
  if (window.MCP_DATA) {
    return window.MCP_DATA as CompanyData
  }

  return {
    company_number: '00445790',
    company_name: 'TESCO PLC',
    company_status: 'active',
    company_type: 'plc',
    date_of_creation: '1947-11-27',
    registered_office_address: {
      address_line_1: 'Tesco House, Shire Park, Kestrel Way',
      locality: 'Welwyn Garden City',
      postal_code: 'AL7 1GA',
      country: 'England'
    },
    sic_codes: ['47110'],
    accounts: {
      next_due: '2025-05-30',
      overdue: false
    },
    confirmation_statement: {
      next_due: '2025-03-25',
      overdue: false
    },
    has_insolvency_history: false,
    has_charges: true,
    data_source: 'Companies House API',
    retrieved_at: new Date().toISOString()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <CompanyInfo data={getData()} />
  </React.StrictMode>
)
