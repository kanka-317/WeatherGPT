import React, { useState } from 'react'
import {
  Sun,
  Cloud,
  CloudRain,
  CloudLightning,
  CloudDrizzle,
  Droplets,
  Wind,
  Compass,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Clock,
  Sparkles,
} from 'lucide-react'

export function getWeatherIcon(condition = 'Clear', className = 'w-6 h-6') {
  const cond = condition.toLowerCase()
  if (cond.includes('thunder') || cond.includes('lightning')) {
    return <CloudLightning className={`${className} text-amber-400 animate-pulse`} />
  } else if (cond.includes('rain') || cond.includes('shower')) {
    return <CloudRain className={`${className} text-cyan-400`} />
  } else if (cond.includes('drizzle')) {
    return <CloudDrizzle className={`${className} text-blue-300`} />
  } else if (cond.includes('cloud') || cond.includes('overcast') || cond.includes('haze')) {
    return <Cloud className={`${className} text-slate-300`} />
  }
  return <Sun className={`${className} text-amber-400 animate-spin-slow`} />
}

export function formatObservationDateTime(timestamp) {
  if (!timestamp) {
    const now = new Date()
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
    const day = String(now.getDate()).padStart(2, '0')
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const year = now.getFullYear()
    return `${time} · ${day}-${month}-${year}`
  }

  let str = String(timestamp).trim()
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str) && !str.endsWith('Z') && !str.includes('+') && !str.slice(10).includes('-')) {
    str += 'Z'
  }

  const d = new Date(str)
  if (isNaN(d.getTime())) {
    return 'Live'
  }

  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${time} · ${day}-${month}-${year}`
}

export default function WeatherCard({
  weatherData,
  forecastData = null,
  onRefresh = null,
  compact = false,
}) {
  const [showForecast, setShowForecast] = useState(false)

  if (!weatherData) return null

  const loc = weatherData.location || {}
  const obs = weatherData.observation || {}
  const alerts = weatherData.alerts || []
  const cached = weatherData.cached
  const cacheAge = weatherData.cache_age_seconds || 0

  return (
    <div className="w-full max-w-xl mx-auto my-2 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-800/80 to-slate-900/90 backdrop-blur-xl border border-cyan-500/20 shadow-2xl shadow-cyan-950/40 overflow-hidden transition-all duration-300 hover:border-cyan-500/40">
      {/* Top Header & Location */}
      <div className="px-5 py-4 flex items-center justify-between border-b border-slate-700/50 bg-slate-800/40">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {getWeatherIcon(obs.condition, 'w-5 h-5')}
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-base flex items-center gap-2">
              {loc.name || 'Selected Location'}
              {loc.state && <span className="text-xs font-normal text-slate-400">({loc.state})</span>}
            </h3>
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5 text-slate-300 font-medium">
                <Clock className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span>{formatObservationDateTime(obs.timestamp)}</span>
              </span>
              <span>•</span>
              <span className="text-cyan-300/80 uppercase font-medium">{obs.source || 'OpenWeather'}</span>
              {cached && (
                <>
                  <span>•</span>
                  <span className="px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">
                    Cached {cacheAge}s ago
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-2xl font-bold tracking-tight text-white flex items-start justify-end">
            {Math.round(obs.temperature ?? 0)}
            <span className="text-sm font-light text-cyan-400 ml-0.5">°C</span>
          </div>
          <p className="text-xs font-medium text-slate-300">{obs.condition || 'Clear'}</p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2 px-5 py-3 bg-slate-900/50 text-center text-xs">
        <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-slate-800/40 border border-slate-700/40">
          <div className="flex items-center gap-1 text-slate-400 mb-1">
            <Droplets className="w-3.5 h-3.5 text-blue-400" />
            <span>Humidity</span>
          </div>
          <span className="font-semibold text-slate-100">{Math.round(obs.humidity ?? 0)}%</span>
        </div>

        <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-slate-800/40 border border-slate-700/40">
          <div className="flex items-center gap-1 text-slate-400 mb-1">
            <Wind className="w-3.5 h-3.5 text-teal-400" />
            <span>Wind</span>
          </div>
          <span className="font-semibold text-slate-100">{obs.wind_speed ?? 0} m/s</span>
        </div>

        <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-slate-800/40 border border-slate-700/40">
          <div className="flex items-center gap-1 text-slate-400 mb-1">
            <CloudRain className="w-3.5 h-3.5 text-cyan-400" />
            <span>Rainfall</span>
          </div>
          <span className="font-semibold text-slate-100">{obs.rainfall ?? 0} mm</span>
        </div>
      </div>

      {/* Severe Weather / Agro Alert Banner */}
      {alerts && alerts.length > 0 && (
        <div className="mx-4 my-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
          <div className="text-xs">
            <div className="font-semibold text-amber-300 flex items-center gap-1.5">
              <span>{alerts[0].type}</span>
              <span className="text-[10px] uppercase px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-200">
                {alerts[0].severity}
              </span>
            </div>
            <p className="text-slate-300 text-[11px] mt-0.5 leading-relaxed">{alerts[0].message}</p>
            <div className="text-[10px] text-amber-400/80 mt-1">Source: {alerts[0].source}</div>
          </div>
        </div>
      )}

      {/* Multi-Day Forecast Expandable Toggle */}
      {forecastData && forecastData.forecast && forecastData.forecast.length > 0 && (
        <div className="border-t border-slate-800">
          <button
            onClick={() => setShowForecast(!showForecast)}
            className="w-full px-5 py-2.5 text-xs text-slate-400 hover:text-cyan-300 flex items-center justify-between transition-colors bg-slate-900/40"
          >
            <span className="flex items-center gap-1.5 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              {showForecast ? 'Hide 3-Day Forecast' : 'View 3-Day Forecast'}
            </span>
            {showForecast ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showForecast && (
            <div className="grid grid-cols-3 gap-2 p-3 bg-slate-950/60 border-t border-slate-800/80 animate-fadeIn">
              {forecastData.forecast.slice(0, 3).map((item, idx) => (
                <div
                  key={idx}
                  className="flex flex-col items-center p-2 rounded-xl bg-slate-900/60 border border-slate-800 text-center"
                >
                  <span className="text-[10px] text-slate-400">
                    {idx === 0 ? 'Today' : idx === 1 ? 'Tomorrow' : `Day ${idx + 1}`}
                  </span>
                  <div className="my-1.5">{getWeatherIcon(item.condition, 'w-5 h-5')}</div>
                  <span className="text-xs font-bold text-white">{Math.round(item.temperature)}°C</span>
                  <span className="text-[10px] text-cyan-300 mt-0.5">
                    {item.rainfall > 0 ? `${item.rainfall}mm` : item.condition}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
