import React from 'react'
import ReactDOM from 'react-dom/client'
import FloodWarnings from './FloodWarnings'
import '@/components/styles.css'
import '@/types'

export interface FloodWarning {
  severity_level: number
  severity: string
  area: string
  description: string
  time_raised: string
  message?: string
}

export interface FloodWarningsData {
  total_warnings: number
  warnings: FloodWarning[]
  data_source: string
  retrieved_at: string
}

const getData = (): FloodWarningsData => {
  if (window.MCP_DATA) {
    return window.MCP_DATA as FloodWarningsData
  }

  return {
    total_warnings: 4,
    warnings: [
      {
        severity_level: 1,
        severity: 'Severe Flood Warning',
        area: 'River Thames at Teddington',
        description: 'Flooding is expected. Immediate action required.',
        time_raised: '2024-01-15T08:30:00Z',
        message: 'River levels are rising rapidly due to heavy rainfall upstream.'
      },
      {
        severity_level: 2,
        severity: 'Flood Warning',
        area: 'River Colne at Watford',
        description: 'Flooding is expected. Prepare to take action.',
        time_raised: '2024-01-15T09:15:00Z'
      },
      {
        severity_level: 3,
        severity: 'Flood Alert',
        area: 'Upper River Lee',
        description: 'Flooding is possible. Be prepared.',
        time_raised: '2024-01-15T07:00:00Z'
      },
      {
        severity_level: 3,
        severity: 'Flood Alert',
        area: 'Grand Union Canal',
        description: 'Flooding is possible. Be prepared.',
        time_raised: '2024-01-15T06:45:00Z'
      }
    ],
    data_source: 'Environment Agency Flood API',
    retrieved_at: new Date().toISOString()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <FloodWarnings data={getData()} />
  </React.StrictMode>
)
