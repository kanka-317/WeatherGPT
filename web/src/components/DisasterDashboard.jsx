import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  AlertTriangle,
  Radio,
  Plus,
  Send,
  CheckCircle2,
  Clock,
  MapPin,
  ExternalLink,
  Sparkles,
  Trash2,
  RefreshCw,
  Layers,
  Flame,
  CloudRain,
  Wind,
  Mountain,
} from 'lucide-react'
import RiskMap, { SEVERITY_COLORS } from './RiskMap'

// Quick Pre-configured Multi-District Demo Scenarios for SIH Judges

const QUICK_DEMO_SCENARIOS = [
  {
    id: 'nadia',
    district: 'Nadia',
    lat: 23.471,
    lon: 88.5565,
    type: 'Heavy Rain & Flash Flood Warning',
    severity: 'Severe',
    icon: '⛈️',
    message:
      'IMD Doppler Radar detected severe storm cloud clusters converging over Nadia district. High risk of waterlogging across agricultural lands.',
    source: 'IMD Doppler Radar Network',
  },
  {
    id: 's24parganas',
    district: 'South 24 Parganas',
    lat: 22.1645,
    lon: 88.6189,
    type: 'Sundarbans Coastal Cyclone Surge Warning',
    severity: 'Extreme',
    icon: '🌀',
    message:
      'Bay of Bengal deep depression intensifying. Gale wind speeds of 85-105 km/h with 2.5m tidal storm surge expected in coastal Sundarbans.',
    source: 'IMD Cyclone Warning Centre',
  },
  {
    id: 'darjeeling',
    district: 'Darjeeling',
    lat: 27.041,
    lon: 88.2663,
    type: 'High-Altitude Landslide & Cloudburst Advisory',
    severity: 'Moderate',
    icon: '⛰️',
    message:
      'Continuous downpour triggering slope instability along NH-10. High risk of debris flow and localized cloudburst in hill sub-divisions.',
    source: 'GSI & IMD Hill Station Ops',
  },
  {
    id: 'kolkata',
    district: 'Kolkata',
    lat: 22.5726,
    lon: 88.3639,
    type: 'Urban Waterlogging & Squall Line Warning',
    severity: 'Severe',
    icon: '🌧️',
    message:
      'Intense convective thundercloud line crossing Greater Kolkata with 50-70 mm/hr rainfall and lightning gusts up to 60 km/h.',
    source: 'IMD Alipore Regional Meteorological Centre',
  },
]

export default function DisasterDashboard({
  backendUrl = 'http://localhost:8000',
  wsAlerts = [],
  wsConnected = false,
}) {
  const [alerts, setAlerts] = useState([])
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [isSimulating, setIsSimulating] = useState(false)
  const [isClearing, setIsClearing] = useState(false)
  const [severityFilter, setSeverityFilter] = useState('all')
  const [showCustomModal, setShowCustomModal] = useState(false)

  // Custom alert form inputs
  const [customForm, setCustomForm] = useState({
    location_name: 'Nadia',
    lat: '23.4710',
    lon: '88.5565',
    type: 'Heavy Rain & Flash Flood Warning',
    severity: 'Severe',
    message:
      'IMD Doppler Radar detects heavy precipitation (75-120 mm) converging over Nadia district. Immediate water drainage advised.',
    source: 'IMD Alipore Regional Centre',
  })

  // Load initial active alerts on mount
  useEffect(() => {
    fetchActiveAlerts()
  }, [])

  // When a new WebSocket alert is pushed from App, update list
  useEffect(() => {
    if (wsAlerts && wsAlerts.length > 0) {
      setAlerts(wsAlerts)
    }
  }, [wsAlerts])

  const fetchActiveAlerts = async () => {
    try {
      const res = await fetch(`${backendUrl}/alerts/active`)
      if (res.ok) {
        const data = await res.json()
        setAlerts(data.alerts || [])
      }
    } catch (err) {
      console.error('Failed to fetch active alerts:', err)
    }
  }

  // Quick Multi-District Trigger
  const handleScenarioTrigger = async (scenario) => {
    setIsSimulating(true)
    try {
      const payload = {
        location_name: scenario.district,
        lat: scenario.lat,
        lon: scenario.lon,
        type: scenario.type,
        severity: scenario.severity,
        message: scenario.message,
        valid_until: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
        source: scenario.source,
      }

      const res = await fetch(`${backendUrl}/alerts/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (res.ok) {
        const newAlert = await res.json()
        setSelectedAlert(newAlert)
        fetchActiveAlerts()
      }
    } catch (err) {
      console.error('Alert simulation error:', err)
    } finally {
      setIsSimulating(false)
    }
  }

  // Clear all demo alerts
  const handleClearAlerts = async () => {
    setIsClearing(true)
    try {
      const res = await fetch(`${backendUrl}/alerts/clear-demo`, {
        method: 'POST',
      })
      if (res.ok) {
        setAlerts([])
        setSelectedAlert(null)
      }
    } catch (err) {
      console.error('Failed to clear alerts:', err)
    } finally {
      setIsClearing(false)
    }
  }

  // Dismiss a single alert
  const handleDismissAlert = async (e, alertId) => {
    e.stopPropagation()
    try {
      const res = await fetch(`${backendUrl}/alerts/${alertId}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        setAlerts((prev) => prev.filter((a) => a.id !== alertId))
        if (selectedAlert?.id === alertId) setSelectedAlert(null)
      }
    } catch (err) {
      console.error('Failed to dismiss alert:', err)
    }
  }

  // Submit custom alert form
  const handleCustomSubmit = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        location_name: customForm.location_name,
        lat: parseFloat(customForm.lat),
        lon: parseFloat(customForm.lon),
        type: customForm.type,
        severity: customForm.severity,
        message: customForm.message,
        source: customForm.source,
        valid_until: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
      }

      const res = await fetch(`${backendUrl}/alerts/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (res.ok) {
        setShowCustomModal(false)
        fetchActiveAlerts()
      }
    } catch (err) {
      console.error('Custom alert error:', err)
    }
  }

  // Filtered alerts
  const filteredAlerts = alerts.filter((alert) => {
    if (severityFilter === 'all') return true
    return (alert.severity || '').toLowerCase() === severityFilter.toLowerCase()
  })

  // Metric aggregates
  const distinctDistricts = Array.from(new Set(alerts.map((a) => a.location_name)))
  const severeCount = alerts.filter((a) => (a.severity || '').toLowerCase() === 'severe').length
  const extremeCount = alerts.filter((a) => (a.severity || '').toLowerCase() === 'extreme').length

  return (
    <div className="w-full space-y-4 animate-fadeIn pb-16">
      {/* Top Banner & Demo Control Center */}
      <div className="p-5 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 shadow-2xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center space-x-3.5">
            <div className="w-11 h-11 rounded-2xl bg-orange-500/10 border border-orange-500/30 text-orange-400 flex items-center justify-center shrink-0 shadow-lg shadow-orange-500/10">
              <Radio className="w-5 h-5 animate-pulse text-orange-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base sm:text-lg font-bold text-white tracking-tight">
                  State Disaster Meteorological Operations Center
                </h2>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1 border ${wsConnected
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                      }`}
                  />
                  {wsConnected ? 'WebSocket Live Feed' : 'Connecting WebSocket...'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time GIS risk mapping & sub-second alert broadcasting layer for West Bengal districts
              </p>
            </div>
          </div>

          {/* Action Tools */}
          <div className="flex items-center gap-2 shrink-0">
            {alerts.length > 0 && (
              <button
                type="button"
                onClick={handleClearAlerts}
                disabled={isClearing}
                title="Clear all test alerts"
                className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-rose-950/40 border border-slate-700 hover:border-rose-500/40 text-slate-300 hover:text-rose-300 text-xs font-medium flex items-center gap-1.5 transition-all shadow-sm"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{isClearing ? 'Clearing...' : 'Clear Test Feed'}</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowCustomModal(true)}
              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-all shadow-sm"
            >
              <Plus className="w-3.5 h-3.5 text-cyan-400" />
              <span>Broadcast Bulletin</span>
            </button>
          </div>
        </div>

        {/* Quick Multi-District Simulation Strip for Hackathon Judges */}
        <div className="pt-3 border-t border-slate-800/80">
          <div className="text-[11px] font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-orange-400" />
            <span>Simulate Real-World IMD Disaster Bulletins (1-Click Judge Demonstrations):</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {QUICK_DEMO_SCENARIOS.map((scenario) => (
              <button
                key={scenario.id}
                type="button"
                onClick={() => handleScenarioTrigger(scenario)}
                disabled={isSimulating}
                className="p-2.5 rounded-xl bg-slate-950/80 hover:bg-slate-850 border border-slate-800 hover:border-orange-500/40 text-left transition-all group disabled:opacity-50"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-slate-200 group-hover:text-orange-300 transition-colors">
                    {scenario.icon} {scenario.district}
                  </span>
                  <span
                    className={`text-[9px] font-bold uppercase px-1.5 py-0.2 rounded border ${scenario.severity === 'Extreme'
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        : 'bg-orange-500/10 text-orange-400 border-orange-500/30'
                      }`}
                  >
                    {scenario.severity}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400 truncate">{scenario.type}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Operational Stats Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Active Bulletins</div>
            <div className="text-xl font-extrabold text-white mt-0.5">{alerts.length}</div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
        </div>

        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">High Risk Districts</div>
            <div className="text-xl font-extrabold text-orange-400 mt-0.5">{distinctDistricts.length}</div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400">
            <MapPin className="w-4 h-4" />
          </div>
        </div>

        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Severe / Extreme</div>
            <div className="text-xl font-extrabold text-rose-400 mt-0.5">{severeCount + extremeCount}</div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <Flame className="w-4 h-4" />
          </div>
        </div>

        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Spatial Engine</div>
            <div className="text-xs font-bold text-emerald-400 mt-1 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>PostGIS ST_DWithin</span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Layers className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Grid: GIS Risk Map on Left, Active Feed on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Map Column */}
        <div className="lg:col-span-7 flex flex-col space-y-2">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>West Bengal Meteorological Risk Layer</span>
            </span>

            {/* Quick jump tags */}
            <div className="hidden sm:flex items-center gap-1 text-[11px] text-slate-400">
              <span className="text-[10px] text-slate-500">Jump:</span>
              {QUICK_DEMO_SCENARIOS.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setSelectedAlert({ lon: s.lon, lat: s.lat })}
                  className="px-2 py-0.5 rounded-md bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-cyan-300 text-[10px] transition-all"
                >
                  {s.district}
                </button>
              ))}
            </div>
          </div>

          <RiskMap
            alerts={filteredAlerts}
            selectedAlert={selectedAlert}
            onSelectAlert={(a) => setSelectedAlert(a)}
          />
        </div>

        {/* Alerts Table Column */}
        <div className="lg:col-span-5 flex flex-col space-y-2">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-orange-400" />
                <span>Active Bulletins ({filteredAlerts.length})</span>
              </span>
            </div>

            <button
              type="button"
              onClick={fetchActiveAlerts}
              className="text-[11px] text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 font-medium"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Refresh</span>
            </button>
          </div>

          {/* Severity Filter Chips */}
          <div className="flex items-center gap-1 p-1 bg-slate-900/80 rounded-xl border border-slate-800 text-[11px]">
            <button
              type="button"
              onClick={() => setSeverityFilter('all')}
              className={`flex-1 py-1 rounded-lg font-medium transition-all ${severityFilter === 'all'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              All ({alerts.length})
            </button>
            <button
              type="button"
              onClick={() => setSeverityFilter('severe')}
              className={`flex-1 py-1 rounded-lg font-medium transition-all ${severityFilter === 'severe'
                  ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                  : 'text-slate-400 hover:text-orange-400'
                }`}
            >
              Severe ({severeCount})
            </button>
            <button
              type="button"
              onClick={() => setSeverityFilter('extreme')}
              className={`flex-1 py-1 rounded-lg font-medium transition-all ${severityFilter === 'extreme'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'text-slate-400 hover:text-rose-400'
                }`}
            >
              Extreme ({extremeCount})
            </button>
          </div>

          {/* Bulletins Scroll View */}
          <div className="h-[445px] overflow-y-auto rounded-2xl bg-slate-900/80 border border-slate-800 p-3 space-y-2.5 shadow-xl">
            {filteredAlerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-6 text-slate-500">
                <CheckCircle2 className="w-10 h-10 text-emerald-500/40 mb-2" />
                <span className="text-xs font-semibold text-slate-300">No Active Bulletins</span>
                <span className="text-[11px] text-slate-500 mt-1 max-w-xs">
                  All districts in this category are operating under normal conditions. Click a simulation
                  button above to test live broadcasting.
                </span>
              </div>
            ) : (
              filteredAlerts.map((alert) => {
                const sevKey = (alert.severity || 'moderate').toLowerCase()
                const color = SEVERITY_COLORS[sevKey] || SEVERITY_COLORS.moderate
                const isSelected = selectedAlert && selectedAlert.id === alert.id

                return (
                  <div
                    key={alert.id}
                    onClick={() => setSelectedAlert(alert)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer text-left group ${isSelected
                        ? 'bg-slate-850 border-cyan-500/60 shadow-xl shadow-cyan-950/40 ring-1 ring-cyan-500/30'
                        : 'bg-slate-950/60 border-slate-800 hover:bg-slate-850 hover:border-slate-700/80'
                      }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2.5 h-2.5 rounded-full shrink-0 shadow-sm"
                          style={{ backgroundColor: color }}
                        />
                        <h4 className="font-bold text-xs text-white group-hover:text-cyan-300 transition-colors">
                          {alert.location_name}
                        </h4>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span
                          className="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border"
                          style={{
                            backgroundColor: `${color}18`,
                            color: color,
                            borderColor: `${color}40`,
                          }}
                        >
                          {alert.severity}
                        </span>

                        <button
                          type="button"
                          onClick={(e) => handleDismissAlert(e, alert.id)}
                          title="Dismiss Bulletin"
                          className="text-slate-600 hover:text-rose-400 p-0.5 rounded transition-colors"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>

                    <div className="text-xs font-semibold text-slate-200 mb-1">{alert.type}</div>
                    <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-2.5">
                      {alert.message}
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-800/80 pt-2">
                      <span className="flex items-center gap-1 text-slate-400">
                        <Clock className="w-3 h-3 text-cyan-400" />
                        Valid till{' '}
                        {new Date(alert.valid_until).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                      <span className="text-cyan-400/90 font-medium flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                        <span>Focus Radar</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </span>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>

      {/* Ingest Custom Alert Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-orange-400" />
                Ingest Official Alert Bulletin
              </h3>
              <button
                type="button"
                onClick={() => setShowCustomModal(false)}
                className="text-slate-400 hover:text-white text-xs"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCustomSubmit} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-3 gap-2.5">
                <div className="col-span-1">
                  <label className="text-slate-400 block mb-1">City / District</label>
                  <input
                    type="text"
                    value={customForm.location_name}
                    onChange={(e) => setCustomForm({ ...customForm, location_name: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Latitude</label>
                  <input
                    type="text"
                    value={customForm.lat}
                    onChange={(e) => setCustomForm({ ...customForm, lat: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Longitude</label>
                  <input
                    type="text"
                    value={customForm.lon}
                    onChange={(e) => setCustomForm({ ...customForm, lon: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="text-slate-400 block mb-1">Alert Type</label>
                  <input
                    type="text"
                    value={customForm.type}
                    onChange={(e) => setCustomForm({ ...customForm, type: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Severity Level</label>
                  <select
                    value={customForm.severity}
                    onChange={(e) => setCustomForm({ ...customForm, severity: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Low">Low (Advisory)</option>
                    <option value="Moderate">Moderate (Watch)</option>
                    <option value="Severe">Severe (Warning)</option>
                    <option value="Extreme">Extreme (Red Alert)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Official Advisory Message</label>
                <textarea
                  rows="3"
                  value={customForm.message}
                  onChange={(e) => setCustomForm({ ...customForm, message: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCustomModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-750"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold transition-all shadow-md shadow-cyan-500/20"
                >
                  Broadcast Alert
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
