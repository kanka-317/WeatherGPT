import React, { useState, useEffect, useRef } from 'react'
import { MapPin, Navigation, Search, X, Check } from 'lucide-react'

const DEMO_CHIPS = [
  { name: 'Kolkata', state: 'WB', lat: 22.5726, lon: 88.3639, icon: '🏛️' },
  { name: 'Nadia', state: 'WB', lat: 23.4710, lon: 88.5565, icon: '🌾' },
  { name: 'S 24 Parganas', state: 'WB', lat: 22.1645, lon: 88.6189, icon: '🌊' },
  { name: 'Darjeeling', state: 'WB', lat: 27.0410, lon: 88.2663, icon: '⛰️' },
  { name: 'Delhi', state: 'NCR', lat: 28.6139, lon: 77.2090, icon: '🏛️' },
  { name: 'Mumbai', state: 'MH', lat: 19.0760, lon: 72.8777, icon: '🏙️' },
]

export default function LocationSearch({
  currentLocation,
  onLocationSelect,
  backendUrl = 'http://localhost:8000',
}) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [gpsLoading, setGpsLoading] = useState(false)
  const dropdownRef = useRef(null)

  // Debounced autocomplete search calling /locations/search?q=
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setSuggestions([])
      return
    }

    const timer = setTimeout(async () => {
      setIsSearching(true)
      try {
        const res = await fetch(`${backendUrl}/locations/search?q=${encodeURIComponent(query.trim())}`)
        if (res.ok) {
          const data = await res.json()
          setSuggestions(data || [])
          setIsOpen(true)
        }
      } catch (err) {
        console.error('Location search failed:', err)
      } finally {
        setIsSearching(false)
      }
    }, 280)

    return () => clearTimeout(timer)
  }, [query, backendUrl])

  // Handle GPS detection
  const handleGPSDetect = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser')
      return
    }
    setGpsLoading(true)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGpsLoading(false)
        onLocationSelect({
          name: `My GPS Location`,
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          isGPS: true,
        })
      },
      (err) => {
        setGpsLoading(false)
        console.warn('GPS detection denied or failed, defaulting to Kolkata:', err)
        onLocationSelect(DEMO_CHIPS[0])
      },
      { timeout: 8000 }
    )
  }

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="w-full flex flex-col space-y-2">
      {/* Top Search & GPS Bar with Glassmorphic Container */}
      <div className="flex items-center gap-2 relative" ref={dropdownRef}>
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-cyan-400/70">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => query.length >= 2 && setIsOpen(true)}
            placeholder="Search any Indian district, city or town..."
            className="w-full pl-9 pr-8 py-2 bg-slate-900/90 hover:bg-slate-900 border border-slate-700/70 hover:border-slate-600 focus:border-cyan-500/80 rounded-xl text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 shadow-inner transition-all"
          />
          {query && (
            <button
              onClick={() => {
                setQuery('')
                setSuggestions([])
              }}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Autocomplete Dropdown */}
          {isOpen && suggestions.length > 0 && (
            <div className="absolute z-50 left-0 right-0 mt-1.5 bg-slate-900/95 border border-slate-700/80 rounded-xl shadow-2xl overflow-hidden backdrop-blur-xl divide-y divide-slate-800/80">
              {suggestions.map((loc, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    onLocationSelect(loc)
                    setQuery(loc.name)
                    setIsOpen(false)
                  }}
                  className="w-full px-3.5 py-2.5 text-left text-xs flex items-center justify-between hover:bg-cyan-500/10 transition-colors group"
                >
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0 group-hover:scale-110 transition-transform" />
                    <div>
                      <span className="font-medium text-slate-200 group-hover:text-cyan-300 transition-colors">
                        {loc.name}
                      </span>
                      {loc.state && <span className="text-[11px] text-slate-400 ml-1.5">({loc.state})</span>}
                    </div>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {loc.lat.toFixed(2)}°N, {loc.lon.toFixed(2)}°E
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* GPS Button */}
        <button
          onClick={handleGPSDetect}
          disabled={gpsLoading}
          title="Detect Current GPS Location"
          className="px-3 py-2 bg-slate-900/90 hover:bg-slate-800 border border-slate-700/70 hover:border-cyan-500/50 rounded-xl text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-all shadow-sm shrink-0 active:scale-95"
        >
          <Navigation className={`w-3.5 h-3.5 ${gpsLoading ? 'animate-spin text-cyan-300' : ''}`} />
          <span className="hidden sm:inline font-medium">GPS</span>
        </button>
      </div>

      {/* Quick Location Chips with Active Indicator */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5 scrollbar-none text-[11px]">
        <div className="flex items-center gap-1 shrink-0 mr-1 text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>Target:</span>
        </div>

        {DEMO_CHIPS.map((chip, idx) => {
          const isSelected =
            currentLocation &&
            Math.abs(currentLocation.lat - chip.lat) < 0.1 &&
            Math.abs(currentLocation.lon - chip.lon) < 0.1

          return (
            <button
              key={idx}
              onClick={() => onLocationSelect(chip)}
              className={`px-2.5 py-1 rounded-lg transition-all shrink-0 flex items-center gap-1.5 text-[11px] font-medium ${
                isSelected
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm shadow-cyan-500/10'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-slate-800'
              }`}
            >
              <span>{chip.icon}</span>
              <span>{chip.name}</span>
              {isSelected && <Check className="w-3 h-3 text-cyan-400" />}
            </button>
          )
        })}

        {currentLocation && (
          <span className="ml-auto text-[10px] font-mono text-slate-500 shrink-0 hidden md:inline">
            📍 {currentLocation.name || 'Selected'} ({currentLocation.lat?.toFixed(2)}°, {currentLocation.lon?.toFixed(2)}°)
          </span>
        )}
      </div>
    </div>
  )
}
