import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import axios from 'axios'

const API = import.meta.env.VITE_MANAGER_API || 'http://localhost:8000'

function App() {
  const [alerts, setAlerts] = useState([])
  useEffect(() => {
    axios.get(`${API}/alerts?limit=100`).then(r => setAlerts(r.data)).catch(console.error)
  }, [])
  return (
    <div style={{padding:20, fontFamily:'Inter, system-ui, Arial'}}>
      <h1>AI-SOC Alerts</h1>
      <p>Showing latest alerts from Manager API.</p>
      <table border="1" cellPadding="6" cellSpacing="0">
        <thead><tr><th>Time</th><th>Rule</th><th>Level</th><th>Tags</th><th>Host</th><th>Message</th></tr></thead>
        <tbody>
          {alerts.map((a, i) => (
            <tr key={i}>
              <td>{a.ts}</td>
              <td>{a.rule_name}</td>
              <td>{a.level}</td>
              <td>{(a.tags||[]).join(', ')}</td>
              <td>{a.event?.host}</td>
              <td style={{maxWidth:600, overflow:'hidden', textOverflow:'ellipsis'}}>{a.event?.message || a.event?.['@raw']}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
