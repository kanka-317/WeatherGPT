import React, { useState, useEffect, useRef } from 'react'
import {
  Send,
  Mic,
  MicOff,
  RotateCcw,
  Sparkles,
  CloudLightning,
  AlertCircle,
  Activity,
  MapPin,
  ShieldAlert,
  MessageSquare,
  Bell,
  X,
  Languages,
  Volume2,
  VolumeX,
  Loader2,
  Info,
  LogOut,
  UserCheck,
} from 'lucide-react'

import WeatherCard from './components/WeatherCard'
import ChatBubble from './components/ChatBubble'
import LocationSearch from './components/LocationSearch'
import SuggestedPrompts from './components/SuggestedPrompts'
import DisasterDashboard from './components/DisasterDashboard'
import AuthPage from './components/AuthPage'
import AboutPage from './components/AboutPage'

const RAW_API_URL = import.meta.env.VITE_API_URL || ''
const BACKEND_URL =
  RAW_API_URL ||
  (typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? `http://${window.location.hostname}:8000`
    : 'https://weathergpt-backend.onrender.com')

const WS_URL =
  import.meta.env.VITE_WS_URL ||
  (BACKEND_URL.startsWith('https://')
    ? BACKEND_URL.replace(/^https:\/\//, 'wss://') + '/ws/alerts'
    : BACKEND_URL.replace(/^http:\/\//, 'ws://') + '/ws/alerts')

const DEFAULT_LOCATION = {
  name: 'Kolkata',
  lat: 22.5726,
  lon: 88.3639,
  state: 'West Bengal',
}

function getOrCreateSessionId() {
  let id = localStorage.getItem('weathergpt_session_id')
  if (!id) {
    id = 'session-' + Math.random().toString(36).substring(2, 10)
    localStorage.setItem('weathergpt_session_id', id)
  }
  return id
}

export default function App() {
  // Authentication State
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('weathergpt_user')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  // Persona Tab Switcher: 'chat' | 'disaster' | 'about'
  const [activeTab, setActiveTab] = useState('chat')

  const [sessionId, setSessionId] = useState(getOrCreateSessionId)
  const [location, setLocation] = useState(DEFAULT_LOCATION)
  const [currentWeather, setCurrentWeather] = useState(null)
  const [forecastData, setForecastData] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const [backendOnline, setBackendOnline] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [language, setLanguage] = useState('en') // 'en' | 'bn' | 'hi'
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')

  // WebSocket Live Alerts State
  const [wsAlerts, setWsAlerts] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [liveToastAlert, setLiveToastAlert] = useState(null)

  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const wsRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioPlayerRef = useRef(null)

  // Auto scroll to bottom in chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    if (activeTab === 'chat') {
      scrollToBottom()
    }
  }, [messages, isLoading, activeTab])

  // Check Backend Health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/health`)
        if (res.ok) {
          setBackendOnline(true)
        } else {
          setBackendOnline(false)
        }
      } catch {
        setBackendOnline(false)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 15000)
    return () => clearInterval(interval)
  }, [])

  // Connect to /ws/alerts WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(WS_URL)
        wsRef.current = ws

        ws.onopen = () => {
          setWsConnected(true)
          console.log('[WebSocket] Connected to live alert feed')
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.event === 'INIT_SNAPSHOT') {
              setWsAlerts(data.alerts || [])
            } else if (data.event === 'NEW_ALERT') {
              const incoming = data.alert
              setWsAlerts((prev) => [incoming, ...prev])
              setLiveToastAlert(incoming)

              // Auto clear toast after 8 seconds
              setTimeout(() => {
                setLiveToastAlert(null)
              }, 8000)
            }
          } catch (e) {
            console.error('[WebSocket] Message parsing error:', e)
          }
        }

        ws.onclose = () => {
          setWsConnected(false)
          // Reconnect after 4 seconds
          setTimeout(connectWebSocket, 4000)
        }

        ws.onerror = (err) => {
          console.warn('[WebSocket] Connection error:', err)
          ws.close()
        }
      } catch (err) {
        console.error('[WebSocket] Setup error:', err)
      }
    }

    connectWebSocket()

    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  // Load weather card data whenever location changes
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const [currRes, foreRes] = await Promise.all([
          fetch(`${BACKEND_URL}/weather/current?lat=${location.lat}&lon=${location.lon}`),
          fetch(`${BACKEND_URL}/weather/forecast?lat=${location.lat}&lon=${location.lon}&days=3`),
        ])

        if (currRes.ok) {
          const curr = await currRes.json()
          setCurrentWeather(curr)
        }
        if (foreRes.ok) {
          const fore = await foreRes.json()
          setForecastData(fore)
        }
      } catch (err) {
        console.error('Failed to load initial weather card:', err)
      }
    }
    fetchWeather()
  }, [location])

  // Load Chat History for Session
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/chat/history?session_id=${sessionId}`)
        if (res.ok) {
          const data = await res.json()
          if (data && data.length > 0) {
            const visible = data
              .filter((m) => m.role === 'user' || m.role === 'assistant')
              .map((m) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                timestamp: m.created_at,
              }))
            setMessages(visible)
          }
        }
      } catch (err) {
        console.error('Failed to load chat history:', err)
      }
    }
    fetchHistory()
  }, [sessionId])

  // Speech Synthesis Playback Function
  const playSpeech = async (textToSpeak, langToUse = language) => {
    if (!textToSpeak) return
    try {
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause()
        audioPlayerRef.current = null
      }
      setIsSpeaking(true)
      const res = await fetch(`${BACKEND_URL}/voice/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: textToSpeak,
          language: langToUse,
        }),
      })

      if (!res.ok) {
        throw new Error(`TTS failed with status ${res.status}`)
      }

      const audioBlob = await res.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      audioPlayerRef.current = audio

      audio.onended = () => setIsSpeaking(false)
      audio.onerror = () => setIsSpeaking(false)
      await audio.play()
    } catch (err) {
      console.warn('[Voice] Audio playback failed or blocked:', err)
      setIsSpeaking(false)
    }
  }

  const stopSpeech = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause()
      audioPlayerRef.current = null
    }
    setIsSpeaking(false)
  }

  // Voice Recording: Browser Web Speech API for real-time streaming STT + fallback to Whisper
  const startVoiceRecording = async () => {
    stopSpeech()
    setInterimTranscript('')

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (SpeechRecognition) {
      try {
        if (recognitionRef.current) {
          try {
            recognitionRef.current.abort()
          } catch (e) {}
        }

        const recognition = new SpeechRecognition()
        recognitionRef.current = recognition
        recognition.lang = language === 'bn' ? 'bn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN'
        recognition.continuous = false
        recognition.interimResults = true

        recognition.onstart = () => {
          setIsListening(true)
          setInterimTranscript('')
        }

        recognition.onresult = (event) => {
          let currentInterim = ''
          let finalTranscript = ''

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const part = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += part
            } else {
              currentInterim += part
            }
          }

          if (currentInterim) {
            setInterimTranscript(currentInterim)
          }

          if (finalTranscript && finalTranscript.trim()) {
            const cleanQuery = finalTranscript.trim()
            setInputMessage(cleanQuery)
            setInterimTranscript('')
            setIsListening(false)

            // Auto-detect language script
            let detectedLang = language
            if (/[\u0980-\u09FF]/.test(cleanQuery)) detectedLang = 'bn'
            else if (/[\u0900-\u097F]/.test(cleanQuery)) detectedLang = 'hi'

            if (['en', 'bn', 'hi'].includes(detectedLang)) {
              setLanguage(detectedLang)
            }

            handleSendMessage(cleanQuery, detectedLang)
          }
        }

        recognition.onerror = (event) => {
          console.warn('[WebSpeech] Recognition error:', event.error)
          if (event.error !== 'no-speech') {
            setIsListening(false)
            setInterimTranscript('')
          }
        }

        recognition.onend = () => {
          setIsListening(false)
        }

        recognition.start()
        return
      } catch (err) {
        console.warn('[WebSpeech] Fallback to MediaRecorder:', err)
      }
    }

    // Fallback: MediaRecorder -> POST /voice/transcribe
    try {
      audioChunksRef.current = []
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        if (audioBlob.size === 0) return

        setIsTranscribing(true)
        try {
          const formData = new FormData()
          formData.append('file', audioBlob, `voice_query_${language}.webm`)

          const res = await fetch(`${BACKEND_URL}/voice/transcribe`, {
            method: 'POST',
            body: formData,
          })

          if (res.ok) {
            const data = await res.json()
            if (data.transcript && data.transcript.trim()) {
              const query = data.transcript.trim()
              setInputMessage(query)
              const detected = data.language || language
              if (['en', 'bn', 'hi'].includes(detected)) {
                setLanguage(detected)
              }
              await handleSendMessage(query, detected)
            }
          }
        } catch (err) {
          console.error('[Voice] Transcription error:', err)
        } finally {
          setIsTranscribing(false)
          setInterimTranscript('')
        }
      }

      recorder.start()
      setIsListening(true)
    } catch (err) {
      console.error('[Voice] MediaRecorder not available:', err)
      alert('Microphone access is unavailable or denied. Please enable mic permissions in your browser.')
      setIsListening(false)
    }
  }

  const stopVoiceRecording = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {}
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop()
      } catch (e) {}
    }
    setIsListening(false)
  }

  const toggleVoiceRecording = () => {
    if (isListening) {
      stopVoiceRecording()
      if (interimTranscript && interimTranscript.trim()) {
        const query = interimTranscript.trim()
        setInputMessage(query)
        handleSendMessage(query, language)
        setInterimTranscript('')
      }
    } else {
      startVoiceRecording()
    }
  }

  // Handle Send Message
  const handleSendMessage = async (textToSend = null, langToSend = language) => {
    const text = textToSend || inputMessage
    if (!text || !text.trim() || isLoading) return

    stopSpeech()

    const userMessageObj = {
      role: 'user',
      content: text.trim(),
      language: langToSend,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessageObj])
    setInputMessage('')
    setIsLoading(true)
    setErrorMsg(null)

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text.trim(),
          session_id: sessionId,
          lat: location.lat,
          lon: location.lon,
          language: langToSend,
        }),
      })

      if (!res.ok) {
        throw new Error(`Server returned error status (${res.status})`)
      }

      const data = await res.json()

      const assistantMessageObj = {
        role: 'assistant',
        content: data.reply,
        tools_called: data.tools_called,
        language: data.language || langToSend,
        timestamp: data.timestamp || new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessageObj])

      // Automatically speak back the assistant's grounded response
      playSpeech(data.reply, data.language || langToSend)
    } catch (err) {
      console.error('Chat error:', err)
      setErrorMsg('Unable to connect to WeatherGPT server. Please verify backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  // Handle Reset Session
  const handleNewSession = () => {
    const newId = 'session-' + Math.random().toString(36).substring(2, 10)
    localStorage.setItem('weathergpt_session_id', newId)
    setSessionId(newId)
    setMessages([])
    setErrorMsg(null)
  }

  // Handle Authentication Callbacks
  const handleLogin = (user) => {
    setCurrentUser(user)
    if (user?.language) {
      setLanguage(user.language)
    }
    if (user?.role === 'disaster_officer') {
      setActiveTab('disaster')
    } else {
      setActiveTab('chat')
    }
  }

  const handleSignOut = () => {
    localStorage.removeItem('weathergpt_user')
    setCurrentUser(null)
    setActiveTab('chat')
  }

  // If unauthenticated, display Sign In / Sign Up View
  if (!currentUser) {
    return <AuthPage onLogin={handleLogin} backendUrl={BACKEND_URL} />
  }

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-slate-950">
      {/* Top Floating Alert Toast Notification for Live Broadcasts */}
      {liveToastAlert && (
        <div className="fixed top-16 right-4 z-50 max-w-sm w-full p-4 rounded-2xl bg-gradient-to-r from-orange-950/95 to-slate-900/95 border-2 border-orange-500/70 shadow-2xl backdrop-blur-xl animate-bounce">
          <div className="flex items-start justify-between gap-2.5">
            <div className="flex items-start gap-2.5">
              <div className="p-2 rounded-xl bg-orange-500/20 text-orange-400">
                <Bell className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-white uppercase">{liveToastAlert.location_name}</span>
                  <span className="px-1.5 py-0.2 rounded bg-orange-500/30 text-orange-300 font-bold text-[10px] uppercase">
                    {liveToastAlert.severity}
                  </span>
                </div>
                <div className="text-xs font-semibold text-orange-200 mt-0.5">{liveToastAlert.type}</div>
                <p className="text-[11px] text-slate-300 line-clamp-2 mt-1">{liveToastAlert.message}</p>
              </div>
            </div>
            <button onClick={() => setLiveToastAlert(null)} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl px-4 py-3 sm:px-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/25">
              <CloudLightning className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-tight text-white">WeatherGPT</h1>
                <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-semibold">
                  SIH PS 26068
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-light">AI Weather Intelligence & GIS Risk Layer</p>
            </div>
          </div>

          {/* Persona View Switcher */}
          <div className="hidden sm:flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1 shadow-inner">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
                activeTab === 'chat'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>AI Chat Assistant</span>
            </button>
            <button
              onClick={() => setActiveTab('disaster')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
                activeTab === 'disaster'
                  ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Disaster Operations Map</span>
              {wsAlerts.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-orange-500 text-slate-950 font-extrabold text-[9px]">
                  {wsAlerts.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('about')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
                activeTab === 'about'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Info className="w-3.5 h-3.5" />
              <span>About & Features</span>
            </button>
          </div>

          {/* Controls & Connection Badges */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Multilingual Selector (EN, BN, HI) */}
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl p-0.5 shadow-inner">
              <button
                type="button"
                onClick={() => setLanguage('en')}
                className={`px-2 py-1 rounded-lg text-xs font-medium transition-all ${
                  language === 'en'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="English"
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => setLanguage('bn')}
                className={`px-2 py-1 rounded-lg text-xs font-medium transition-all ${
                  language === 'bn'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="বাংলা (Bengali)"
              >
                বাংলা
              </button>
              <button
                type="button"
                onClick={() => setLanguage('hi')}
                className={`px-2 py-1 rounded-lg text-xs font-medium transition-all ${
                  language === 'hi'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="हिन्दी (Hindi)"
              >
                हिन्दी
              </button>
            </div>

            <div
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
                backendOnline
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="hidden sm:inline">{backendOnline ? 'Backend Online' : 'Connecting...'}</span>
            </div>

            {activeTab === 'chat' && (
              <button
                onClick={handleNewSession}
                title="Start New Session"
                className="p-1.5 sm:px-2.5 sm:py-1 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/60 text-slate-300 hover:text-white text-xs flex items-center gap-1.5 transition-all shadow-sm"
              >
                <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
                <span className="hidden sm:inline">New Chat</span>
              </button>
            )}

            {/* User Profile & Sign Out Button */}
            <div className="flex items-center gap-1.5 pl-1 sm:pl-2 border-l border-slate-800">
              <div
                title={`${currentUser.name} (${currentUser.role})`}
                className="hidden md:flex items-center gap-1.5 px-2 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                <span className="font-medium text-slate-200 truncate max-w-[100px]">{currentUser.name}</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono uppercase">
                  {currentUser.role === 'disaster_officer' ? 'DM' : currentUser.role === 'researcher' ? 'SCI' : 'CIT'}
                </span>
              </div>
              <button
                onClick={handleSignOut}
                title="Sign Out / Switch Account"
                className="p-1.5 sm:px-2.5 sm:py-1 rounded-xl bg-slate-900 hover:bg-rose-950/40 hover:text-rose-300 border border-slate-800 hover:border-rose-500/30 text-slate-400 transition-all flex items-center gap-1.5 text-xs"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden lg:inline">Sign Out</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Tab Switcher */}
        <div className="flex sm:hidden items-center justify-center mt-2.5 bg-slate-900 border border-slate-800 rounded-xl p-1 gap-1">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-1 rounded-lg text-xs font-medium flex items-center justify-center gap-1 ${
              activeTab === 'chat' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Chat</span>
          </button>
          <button
            onClick={() => setActiveTab('disaster')}
            className={`flex-1 py-1 rounded-lg text-xs font-medium flex items-center justify-center gap-1 ${
              activeTab === 'disaster' ? 'bg-orange-500/20 text-orange-300' : 'text-slate-400'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Map ({wsAlerts.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`flex-1 py-1 rounded-lg text-xs font-medium flex items-center justify-center gap-1 ${
              activeTab === 'about' ? 'bg-purple-500/20 text-purple-300' : 'text-slate-400'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>About</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-3 sm:p-6 flex flex-col space-y-4">
        {activeTab === 'about' ? (
          /* Persona: About & Features */
          <AboutPage onNavigateTab={(tab) => setActiveTab(tab)} />
        ) : activeTab === 'disaster' ? (
          /* Persona: Disaster Manager Center */
          <DisasterDashboard
            backendUrl={BACKEND_URL}
            wsAlerts={wsAlerts}
            wsConnected={wsConnected}
          />
        ) : (
          /* Persona: Citizen / Farmer AI Weather Assistant */
          <>
            {/* Location Selector & Quick Chips */}
            <section className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-3.5 sm:p-4 backdrop-blur-md shadow-xl">
              <LocationSearch
                currentLocation={location}
                onLocationSelect={(loc) => setLocation(loc)}
                backendUrl={BACKEND_URL}
              />
            </section>

            {/* Live Weather Card */}
            {currentWeather && (
              <section className="animate-fadeIn">
                <WeatherCard weatherData={currentWeather} forecastData={forecastData} />
              </section>
            )}

            {/* Chat Stream Area */}
            <section className="flex-1 flex flex-col space-y-2 pb-24">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center my-auto py-8 px-4 text-center">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-3 shadow-inner">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <h2 className="text-base font-semibold text-slate-200">How can I assist your weather needs today?</h2>
                  <p className="text-xs text-slate-400 max-w-md mt-1 mb-4">
                    Ask about live rainfall, 5-day forecasts, irrigation schedules, or meteorological warnings.
                  </p>

                  <div className="w-full max-w-xl">
                    <SuggestedPrompts
                      onSelectPrompt={(p) => handleSendMessage(p, language)}
                      language={language}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex flex-col space-y-2">
                  {messages.map((msg, index) => (
                    <ChatBubble key={index} message={msg} onSpeak={playSpeech} />
                  ))}
                </div>
              )}

              {/* Speaking Voice Response Bar */}
              {isSpeaking && (
                <div className="flex items-center justify-between gap-3 p-2.5 px-3 max-w-sm rounded-xl bg-cyan-950/80 border border-cyan-500/40 text-xs text-cyan-300 backdrop-blur-md animate-pulse">
                  <div className="flex items-center gap-2">
                    <Volume2 className="w-4 h-4 text-cyan-400 animate-bounce" />
                    <span>Speaking response / অডিও বাজছে...</span>
                  </div>
                  <button
                    onClick={stopSpeech}
                    className="p-1 rounded-lg bg-cyan-900/60 hover:bg-cyan-800 text-cyan-200 text-[10px] font-semibold flex items-center gap-1"
                  >
                    <VolumeX className="w-3 h-3" />
                    Stop
                  </button>
                </div>
              )}

              {/* Transcribing Voice Audio Indicator */}
              {isTranscribing && (
                <div className="flex items-center gap-2.5 p-2.5 px-3 max-w-sm rounded-xl bg-purple-950/80 border border-purple-500/40 text-xs text-purple-300 backdrop-blur-md animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                  <span>Processing voice with Whisper... / কণ্ঠস্বর অনুবাদ হচ্ছে...</span>
                </div>
              )}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex items-center gap-3 p-3.5 max-w-md rounded-2xl bg-slate-900/80 border border-cyan-500/30 text-xs text-cyan-300 backdrop-blur-md animate-fadeIn">
                  <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin shrink-0" />
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium">
                      {language === 'bn'
                        ? 'WeatherGPT আবহাওয়া বিশ্লেষণ করছে...'
                        : language === 'hi'
                        ? 'WeatherGPT मौसम का विश्लेषण कर रहा है...'
                        : 'WeatherGPT is evaluating meteorological models...'}
                    </span>
                  </div>
                </div>
              )}

              {/* Error Banner */}
              {errorMsg && (
                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-300 flex items-start gap-2.5 animate-fadeIn">
                  <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p>{errorMsg}</p>
                    <button
                      onClick={() => handleSendMessage()}
                      className="mt-1.5 underline font-medium text-red-200 hover:text-white"
                    >
                      Retry request
                    </button>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </section>
          </>
        )}
      </main>

      {/* Floating Bottom Input Bar for Chat Mode */}
      {activeTab === 'chat' && (
        <footer className="fixed bottom-0 left-0 right-0 z-40 bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent pb-4 pt-6 px-4">
          <div className="max-w-4xl mx-auto">
            {/* Live Voice Recording Status Banner */}
            {isListening && (
              <div className="mb-2.5 px-3.5 py-2.5 rounded-2xl bg-slate-900/95 border border-rose-500/50 shadow-xl shadow-rose-500/20 backdrop-blur-xl flex items-center justify-between gap-3 animate-in fade-in slide-in-from-bottom-2 duration-200">
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <span className="relative flex h-3 w-3 shrink-0">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                  </span>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-[11px] font-bold text-rose-300 uppercase tracking-wide">
                      {language === 'bn' ? 'শুনছি...' : language === 'hi' ? 'सुन रहा हूँ...' : 'Listening...'}
                    </span>
                    <div className="flex items-center gap-0.5">
                      <span className="w-1 h-3 bg-rose-400 rounded-full animate-pulse"></span>
                      <span className="w-1 h-4 bg-rose-300 rounded-full animate-bounce"></span>
                      <span className="w-1 h-2 bg-rose-500 rounded-full animate-pulse"></span>
                      <span className="w-1 h-5 bg-rose-400 rounded-full animate-bounce"></span>
                    </div>
                  </div>
                  <div className="text-xs text-slate-200 truncate italic flex-1">
                    {interimTranscript ? (
                      <span className="text-cyan-300 font-medium">"{interimTranscript}"</span>
                    ) : (
                      <span className="text-slate-400">
                        {language === 'bn'
                          ? 'আপনার প্রশ্নটি বলুন (যেমন: "আজকের তাপমাত্রা কত?")...'
                          : language === 'hi'
                          ? 'अपना प्रश्न बोलें (जैसे: "आज का तापमान कितना है?")...'
                          : 'Speak your question (e.g. "What is the temperature today?")...'}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => {
                      stopVoiceRecording()
                      const queryToSend = (interimTranscript || inputMessage).trim()
                      if (queryToSend) {
                        setInputMessage(queryToSend)
                        handleSendMessage(queryToSend, language)
                        setInterimTranscript('')
                      }
                    }}
                    className="px-3 py-1 text-xs font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl transition-all shadow-md flex items-center gap-1.5 active:scale-95"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{language === 'bn' ? 'পাঠান' : language === 'hi' ? 'भेजें' : 'Send & Ask'}</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      stopVoiceRecording()
                      setInterimTranscript('')
                    }}
                    className="px-2.5 py-1 text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-xl transition-all"
                  >
                    {language === 'bn' ? 'বাতিল' : language === 'hi' ? 'रद्द' : 'Cancel'}
                  </button>
                </div>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleSendMessage()
              }}
              className="flex items-center gap-2 p-1.5 bg-slate-900/95 border border-slate-700/80 rounded-2xl shadow-2xl backdrop-blur-xl focus-within:border-cyan-500/60 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all"
            >
              {/* Voice Record Button */}
              <button
                type="button"
                onClick={toggleVoiceRecording}
                disabled={isTranscribing}
                title={
                  isListening
                    ? 'Recording... Click to stop and transcribe'
                    : 'Speak by voice (Whisper)'
                }
                className={`p-2.5 rounded-xl transition-all shrink-0 relative ${
                  isListening
                    ? 'bg-rose-500 text-white animate-pulse shadow-lg shadow-rose-500/40 ring-4 ring-rose-500/20'
                    : isTranscribing
                    ? 'bg-purple-600 text-white animate-pulse'
                    : 'bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-cyan-300'
                }`}
              >
                {isTranscribing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : isListening ? (
                  <MicOff className="w-4 h-4" />
                ) : (
                  <Mic className="w-4 h-4" />
                )}
              </button>

              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={
                  language === 'bn'
                    ? `${location.name}-এর আবহাওয়া সম্পর্কে জিজ্ঞাসা করুন... (যেমন "কাল বৃষ্টি হবে?")`
                    : language === 'hi'
                    ? `${location.name} के मौसम के बारे में पूछें... (जैसे "कल बारिश होगी?")`
                    : `Ask WeatherGPT about ${location.name}... (e.g. "Will it rain tomorrow?")`
                }
                disabled={isLoading || isTranscribing}
                className="flex-1 bg-transparent px-2 py-2 text-xs sm:text-sm text-slate-100 placeholder-slate-400 focus:outline-none"
              />

              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md shadow-cyan-500/25 shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="text-[10px] text-center text-slate-500 mt-1.5 font-light flex items-center justify-center gap-2">
              <span>SIH PS 26068</span>
              <span>·</span>
              <span className="text-cyan-400 font-medium">
                {language === 'bn' ? 'বাংলা ভয়েস সক্রিয়' : language === 'hi' ? 'हिन्दी वॉइस सक्रिय' : 'Voice & Multilingual Active'}
              </span>
              <span>·</span>
              <span>OpenWeather & IMD Grounded</span>
            </div>
          </div>
        </footer>
      )}
    </div>
  )
}
