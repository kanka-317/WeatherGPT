import React, { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Layers, Maximize2, RotateCcw, ShieldAlert, Sparkles, Navigation } from 'lucide-react'

// Severity to Hex Color & Badge styling
export const SEVERITY_COLORS = {
  low: '#10B981',        // Emerald Green
  advisory: '#10B981',
  moderate: '#FBBF24',   // Amber Yellow
  watch: '#FBBF24',
  severe: '#F97316',     // Bright Orange
  warning: '#F97316',
  extreme: '#EF4444',    // Crimson Red
  emergency: '#EF4444',
}

// 100% Reliable MapLibre Raster Styles (Zero Vector/Font WebGL loading failures)
const MAP_STYLES = {
  dark: {
    id: 'dark',
    name: 'Dark Canvas',
    icon: '🌑',
    style: {
      version: 8,
      sources: {
        'esri-dark-base': {
          type: 'raster',
          tiles: [
            'https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
          ],
          tileSize: 256,
          attribution: '&copy; Esri, HERE, Garmin, (c) OpenStreetMap contributors',
        },
        'esri-dark-reference': {
          type: 'raster',
          tiles: [
            'https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
          ],
          tileSize: 256,
          attribution: '&copy; Esri',
        },
      },
      layers: [
        {
          id: 'esri-dark-base-layer',
          type: 'raster',
          source: 'esri-dark-base',
          minzoom: 0,
          maxzoom: 18,
        },
        {
          id: 'esri-dark-reference-layer',
          type: 'raster',
          source: 'esri-dark-reference',
          minzoom: 0,
          maxzoom: 18,
        },
      ],
    },
  },
  satellite: {
    id: 'satellite',
    name: 'Satellite View',
    icon: '🛰️',
    style: {
      version: 8,
      sources: {
        'esri-satellite': {
          type: 'raster',
          tiles: [
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          ],
          tileSize: 256,
          attribution: '&copy; Esri World Imagery',
        },
      },
      layers: [
        {
          id: 'esri-satellite-layer',
          type: 'raster',
          source: 'esri-satellite',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
  },
  voyager: {
    id: 'voyager',
    name: 'Topography',
    icon: '🗺️',
    style: {
      version: 8,
      sources: {
        'esri-topo': {
          type: 'raster',
          tiles: [
            'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
          ],
          tileSize: 256,
          attribution: '&copy; Esri World Topo Map',
        },
      },
      layers: [
        {
          id: 'esri-topo-layer',
          type: 'raster',
          source: 'esri-topo',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
  },
}

// Generate Geodesic Circle polygon for radar risk buffer
function createGeoJSONCircle(centerLon, centerLat, radiusKm = 32, points = 48) {
  const coords = []
  const distanceX = radiusKm / (111.32 * Math.cos((centerLat * Math.PI) / 180))
  const distanceY = radiusKm / 110.574

  for (let i = 0; i <= points; i++) {
    const theta = (i / points) * (2 * Math.PI)
    const x = distanceX * Math.cos(theta)
    const y = distanceY * Math.sin(theta)
    coords.push([centerLon + x, centerLat + y])
  }

  return coords
}

export default function RiskMap({ alerts = [], selectedAlert = null, onSelectAlert = null }) {
  const mapContainer = useRef(null)
  const mapRef = useRef(null)
  const markersRef = useRef([])
  const [activeBasemap, setActiveBasemap] = useState('dark')
  const [centerCoords, setCenterCoords] = useState({ lat: 23.2, lon: 88.36 })

  // Initialize Map instance
  useEffect(() => {
    if (mapRef.current) return

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: MAP_STYLES.dark.style,
      center: [88.3639, 23.2], // West Bengal Region
      zoom: 7.2,
      attributionControl: false,
    })

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right')

    map.on('move', () => {
      const c = map.getCenter()
      setCenterCoords({ lat: c.lat, lon: c.lng })
    })

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  // Change Basemap Style dynamically
  const switchBasemap = (styleKey) => {
    const map = mapRef.current
    if (!map || activeBasemap === styleKey) return

    setActiveBasemap(styleKey)
    map.setStyle(MAP_STYLES[styleKey].style)

    // Re-add threat zones after style load
    map.once('style.load', () => {
      renderRadarThreatZones(map, alerts)
    })
  }

  // Draw Doppler Radar Hazard Zones
  const renderRadarThreatZones = (map, alertList) => {
    if (!map) return

    // Remove old layers & sources if they exist
    if (map.getLayer('threat-zone-fill')) map.removeLayer('threat-zone-fill')
    if (map.getLayer('threat-zone-stroke')) map.removeLayer('threat-zone-stroke')
    if (map.getSource('threat-zones')) map.removeSource('threat-zones')

    if (!alertList || alertList.length === 0) return

    const features = alertList.map((alert, idx) => {
      const sevKey = (alert.severity || 'moderate').toLowerCase()
      const color = SEVERITY_COLORS[sevKey] || SEVERITY_COLORS.moderate
      const ringCoords = createGeoJSONCircle(alert.lon, alert.lat, 35)

      return {
        type: 'Feature',
        properties: {
          id: alert.id || idx,
          severity: alert.severity,
          color: color,
        },
        geometry: {
          type: 'Polygon',
          coordinates: [ringCoords],
        },
      }
    })

    map.addSource('threat-zones', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: features,
      },
    })

    map.addLayer({
      id: 'threat-zone-fill',
      type: 'fill',
      source: 'threat-zones',
      paint: {
        'fill-color': ['get', 'color'],
        'fill-opacity': 0.18,
      },
    })

    map.addLayer({
      id: 'threat-zone-stroke',
      type: 'line',
      source: 'threat-zones',
      paint: {
        'line-color': ['get', 'color'],
        'line-width': 1.8,
        'line-opacity': 0.75,
        'line-dasharray': [3, 2],
      },
    })
  }

  // Sync Markers & Radar Buffers with Alerts
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove())
    markersRef.current = []

    // Count coordinates to apply offset to duplicates so they don't block each other
    const coordCounts = {}
    alerts.forEach((a) => {
      const k = `${a.lat.toFixed(2)}_${a.lon.toFixed(2)}`
      coordCounts[k] = (coordCounts[k] || 0) + 1
    })

    const groupTracker = {}

    alerts.forEach((alert) => {
      const sevKey = (alert.severity || 'moderate').toLowerCase()
      const color = SEVERITY_COLORS[sevKey] || SEVERITY_COLORS.moderate

      // Coordinate offset for duplicates (e.g. repeated Nadia alerts)
      const coordKey = `${alert.lat.toFixed(2)}_${alert.lon.toFixed(2)}`
      let renderLon = alert.lon
      let renderLat = alert.lat

      if (coordCounts[coordKey] > 1) {
        const offsetIndex = groupTracker[coordKey] || 0
        groupTracker[coordKey] = offsetIndex + 1
        const angle = (offsetIndex / coordCounts[coordKey]) * (2 * Math.PI)
        const radius = 0.055 // ~6 km visual offset
        renderLon = alert.lon + Math.cos(angle) * radius
        renderLat = alert.lat + Math.sin(angle) * radius
      }

      // Create Custom Animated Marker Element
      const el = document.createElement('div')
      el.className = 'relative flex items-center justify-center cursor-pointer group'

      // Outer animated pulse ring
      const ring = document.createElement('div')
      ring.className = 'absolute w-8 h-8 rounded-full animate-ping opacity-60'
      ring.style.backgroundColor = color

      // Intermediate threat glow
      const glow = document.createElement('div')
      glow.className = 'absolute w-6 h-6 rounded-full opacity-40 blur-sm'
      glow.style.backgroundColor = color

      // Center solid badge with hazard icon
      const pin = document.createElement('div')
      pin.className =
        'relative w-5 h-5 rounded-full border-2 border-white shadow-xl flex items-center justify-center text-[9px] font-black text-white transition-all transform group-hover:scale-130'
      pin.style.backgroundColor = color
      pin.innerText = alert.location_name ? alert.location_name[0] : '!'

      el.appendChild(ring)
      el.appendChild(glow)
      el.appendChild(pin)

      // Create Detailed Glassmorphic Popup
      const popupHTML = `
        <div style="color: #f8fafc; font-family: ui-sans-serif, system-ui, sans-serif; min-width: 210px; padding: 4px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px;">
            <strong style="font-size: 13px; color: #38bdf8; display: flex; align-items: center; gap: 4px;">
              📍 ${alert.location_name}
            </strong>
            <span style="font-size: 9px; font-weight: 800; text-transform: uppercase; background: ${color}25; color: ${color}; padding: 2px 7px; border-radius: 9999px; border: 1px solid ${color}60;">
              ${alert.severity}
            </span>
          </div>
          <div style="font-size: 12px; font-weight: 700; margin-bottom: 4px; color: #e2e8f0; line-height: 1.3;">
            ${alert.type}
          </div>
          <p style="font-size: 11px; color: #cbd5e1; line-height: 1.45; margin: 0 0 8px 0; max-height: 90px; overflow-y: auto;">
            ${alert.message}
          </p>
          <div style="font-size: 9px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 5px; display: flex; justify-content: space-between;">
            <span>🛡️ ${alert.source || 'IMD Network'}</span>
            <span>⏱️ Valid: ${new Date(alert.valid_until).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      `

      const popup = new maplibregl.Popup({
        offset: 16,
        closeButton: false,
        className: 'custom-map-popup',
      }).setHTML(popupHTML)

      el.addEventListener('click', () => {
        if (onSelectAlert) onSelectAlert(alert)
      })

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([renderLon, renderLat])
        .setPopup(popup)
        .addTo(map)

      markersRef.current.push(marker)
    })

    // Draw / Update radar hazard zones on map
    if (map.isStyleLoaded()) {
      renderRadarThreatZones(map, alerts)
    } else {
      map.once('style.load', () => renderRadarThreatZones(map, alerts))
    }
  }, [alerts, onSelectAlert])

  // Fly to Selected Alert
  useEffect(() => {
    if (selectedAlert && mapRef.current) {
      mapRef.current.flyTo({
        center: [selectedAlert.lon, selectedAlert.lat],
        zoom: 9.0,
        speed: 1.2,
        curve: 1.4,
        essential: true,
      })
    }
  }, [selectedAlert])

  // Recenter Map on West Bengal
  const handleRecenter = () => {
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [88.3639, 23.2],
        zoom: 7.2,
        speed: 1.2,
      })
    }
  }

  // Fit All Active Alerts inside viewport
  const handleFitBounds = () => {
    if (!mapRef.current || alerts.length === 0) return
    const bounds = new maplibregl.LngLatBounds()
    alerts.forEach((a) => bounds.extend([a.lon, a.lat]))
    mapRef.current.fitBounds(bounds, { padding: 60, maxZoom: 10 })
  }

  return (
    <div className="relative w-full h-[490px] rounded-3xl overflow-hidden border border-slate-700/80 shadow-2xl bg-slate-950">
      {/* Map Container */}
      <div ref={mapContainer} className="w-full h-full" />

      {/* Top Floating Map Controls Bar */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap items-center gap-1.5 p-1 bg-slate-900/90 backdrop-blur-xl border border-slate-700/70 rounded-2xl shadow-xl">
        {/* Basemap Switcher */}
        {Object.values(MAP_STYLES).map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => switchBasemap(s.id)}
            className={`px-2.5 py-1 rounded-xl text-[11px] font-medium flex items-center gap-1.5 transition-all ${
              activeBasemap === s.id
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <span>{s.icon}</span>
            <span className="hidden sm:inline">{s.name}</span>
          </button>
        ))}

        <div className="w-[1px] h-4 bg-slate-700 mx-0.5" />

        {/* Fit Bounds Button */}
        {alerts.length > 0 && (
          <button
            type="button"
            onClick={handleFitBounds}
            title="Zoom to Fit All Alerts"
            className="px-2.5 py-1 rounded-xl text-[11px] font-medium bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-white flex items-center gap-1 transition-all"
          >
            <Maximize2 className="w-3 h-3 text-cyan-400" />
            <span className="hidden md:inline">Fit Alerts</span>
          </button>
        )}

        {/* Recenter Bengal Button */}
        <button
          type="button"
          onClick={handleRecenter}
          title="Reset to West Bengal Center"
          className="px-2.5 py-1 rounded-xl text-[11px] font-medium bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-white flex items-center gap-1 transition-all"
        >
          <RotateCcw className="w-3 h-3 text-slate-400" />
          <span className="hidden md:inline">Bengal</span>
        </button>
      </div>

      {/* Coordinate HUD indicator */}
      <div className="absolute top-3 right-14 z-10 hidden sm:flex items-center gap-1 px-2.5 py-1 bg-slate-900/80 backdrop-blur-md border border-slate-700/60 rounded-xl text-[10px] font-mono text-slate-400">
        <Navigation className="w-2.5 h-2.5 text-cyan-400" />
        <span>
          {centerCoords.lat.toFixed(2)}°N, {centerCoords.lon.toFixed(2)}°E
        </span>
      </div>

      {/* Radar Doppler Legend Overlay */}
      <div className="absolute bottom-3 left-3 bg-slate-900/95 backdrop-blur-xl border border-slate-700/80 rounded-2xl p-3 shadow-2xl text-[11px] space-y-1.5 z-10 max-w-[210px]">
        <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 mb-1.5">
          <span className="font-bold text-slate-200 text-[10px] uppercase tracking-wider flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-orange-400" />
            IMD Risk Scale
          </span>
          <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/60 px-1.5 py-0.2 rounded border border-cyan-500/20">
            35km Radar
          </span>
        </div>

        <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-[10px]">
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0 shadow-sm shadow-emerald-500/50" />
            <span>Advisory</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0 shadow-sm shadow-amber-400/50" />
            <span>Watch</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-orange-500 shrink-0 shadow-sm shadow-orange-500/50" />
            <span>Warning</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-red-500 shrink-0 shadow-sm shadow-red-500/50" />
            <span>Extreme</span>
          </div>
        </div>
      </div>
    </div>
  )
}
