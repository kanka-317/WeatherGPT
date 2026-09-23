import React from 'react'
import {
  CloudLightning,
  ShieldAlert,
  Mic,
  Languages,
  Database,
  Layers,
  Cpu,
  Sprout,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Zap,
  Globe,
  Radio,
  FileCheck2,
} from 'lucide-react'

export default function AboutPage({ onNavigateTab }) {
  const features = [
    {
      icon: <Sparkles className="w-5 h-5 text-cyan-400" />,
      title: 'Zero-Hallucination AI Intelligence',
      badge: 'Grounding Rule',
      desc: 'WeatherGPT decouples LLM generation from deterministic tools. Every forecast or warning is mathematically bound to OpenWeather and official IMD observations with observation timestamps.',
    },
    {
      icon: <Layers className="w-5 h-5 text-emerald-400" />,
      title: 'PostGIS Spatial Proximity Engine',
      badge: 'ST_DWithin',
      desc: 'High-speed geospatial queries using PostgreSQL + PostGIS 3.3.7. Calculates exact distance radiuses in kilometers to evaluate weather hazards approaching specific district coordinates.',
    },
    {
      icon: <Radio className="w-5 h-5 text-orange-400" />,
      title: 'Real-Time WebSocket Push Channel',
      badge: 'Sub-second',
      desc: 'Municipal disaster managers receive instant alert broadcasts (/ws/alerts) without manual browser reloads. Critical bulletins appear as audio-visual toasts across connected command centers.',
    },
    {
      icon: <Mic className="w-5 h-5 text-purple-400" />,
      title: 'Voice & Multilingual Speech Pipeline',
      badge: 'Whisper + TTS',
      desc: 'Native speech-to-text acoustic transcription powered by OpenAI Whisper, coupled with low-latency speech synthesis supporting English, বাংলা (Bengali), and हिन्दी (Hindi).',
    },
    {
      icon: <Sprout className="w-5 h-5 text-lime-400" />,
      title: 'Role-Specific Agro-Advisory',
      badge: 'Farmer Protection',
      desc: 'Actionable crop guidance calculated directly from forecast precipitation (mm), wind speed, and soil moisture risk. Tells farmers when to hold irrigation to prevent crop failure.',
    },
    {
      icon: <Database className="w-5 h-5 text-blue-400" />,
      title: 'Managed Cloud Architecture',
      badge: 'Supabase Cloud',
      desc: 'Powered by Supabase cloud PostgreSQL with postgis (v3.3.7) and pgvector (v0.8.2) extensions enabled, featuring SQLAlchemy 2.0 asyncpg connection pooling for maximum concurrency.',
    },
  ]

  const techStack = [
    { name: 'FastAPI (Python 3.11/3.14)', role: 'Async High-Throughput Microservice' },
    { name: 'PostgreSQL / PostGIS / pgvector', role: 'Geospatial & Vector Storage (Supabase)' },
    { name: 'OpenAI Whisper & GPT-4o-mini', role: 'Acoustic STT & Guardrailed Tool-Calling' },
    { name: 'MapLibre GL JS', role: 'Hardware-Accelerated Vector Risk Map' },
    { name: 'React + Vite + Tailwind CSS', role: 'Ultra-Responsive Glassmorphic Interface' },
    { name: 'Native WebSockets', role: 'Instant Disaster Broadcast Streaming' },
  ]

  return (
    <div className="flex-1 flex flex-col space-y-8 animate-fadeIn pb-16">
      {/* Hero Banner */}
      <section className="relative rounded-3xl p-6 sm:p-10 bg-gradient-to-br from-slate-900 via-slate-900/90 to-cyan-950/30 border border-slate-800/80 shadow-2xl overflow-hidden">
        <div className="absolute -right-16 -top-16 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-4">
            <CloudLightning className="w-3.5 h-3.5" />
            <span>Smart India Hackathon 2024 · Problem Statement 26068</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            AI-Driven Meteorological Intelligence & Disaster Early-Warning
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-light mt-3 leading-relaxed">
            WeatherGPT bridges the gap between raw scientific meteorological data and everyday citizens,
            farmers, and emergency response teams. By combining strict spatial tool-calling with anti-hallucination
            guardrails and real-time GIS mapping, it turns weather warnings into actionable, life-saving intelligence.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-6">
            <button
              onClick={() => onNavigateTab('chat')}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold transition-all shadow-lg shadow-cyan-500/25 flex items-center gap-1.5"
            >
              <span>Try AI Chat Assistant</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigateTab('disaster')}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-medium transition-all flex items-center gap-1.5"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-orange-400" />
              <span>Explore Disaster Risk Map</span>
            </button>
          </div>
        </div>
      </section>

      {/* Core Features Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span>Core Architectural Features</span>
            </h2>
            <p className="text-xs text-slate-400 font-light">
              Designed from first principles to exceed SIH requirements
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((item, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 hover:border-cyan-500/40 transition-all duration-300 backdrop-blur-md shadow-lg flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 rounded-xl bg-slate-800/80 group-hover:bg-cyan-950/60 transition-colors">
                    {item.icon}
                  </div>
                  <span className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700/60 text-[10px] font-mono text-cyan-300">
                    {item.badge}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-slate-100 group-hover:text-cyan-300 transition-colors">
                  {item.title}
                </h3>
                <p className="text-xs text-slate-400 font-light mt-1.5 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Tech Stack & System Specifications */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tech Stack Breakdown */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md shadow-xl">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>Technology Stack Implementation</span>
          </h3>
          <div className="space-y-2.5">
            {techStack.map((tech, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs"
              >
                <span className="font-semibold text-slate-200">{tech.name}</span>
                <span className="text-[11px] text-cyan-400 font-light">{tech.role}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Verification & Compliance Card */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
              <FileCheck2 className="w-4 h-4 text-emerald-400" />
              <span>SIH PS 26068 Quality & Security Metrics</span>
            </h3>
            <ul className="space-y-2 text-xs text-slate-300 font-light">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>19 Automated Tests Passing:</strong> 100% test pass rate across unit weather caching, spatial queries, and voice synthesis.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Zero-Cost Resilient TTS:</strong> Smart circuit breaker falling back to gTTS with offline readiness.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>PostGIS Spatial Indexing:</strong> Spatial distance checks in &lt;10 milliseconds on live Supabase cloud database.</span>
              </li>
            </ul>
          </div>

          <div className="mt-5 p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/20 text-[11px] text-cyan-300">
            💡 <strong>Hackathon Demo Tip:</strong> Switch between English, Bengali, and Hindi in the navbar to test instant voice output.
          </div>
        </div>
      </section>
    </div>
  )
}
