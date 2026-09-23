import React from 'react'
import { Bot, User, Zap, Volume2 } from 'lucide-react'
import WeatherCard from './WeatherCard'

function formatMessageTime(timestamp) {
  if (!timestamp) return 'Just now'
  let str = String(timestamp).trim()
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str) && !str.endsWith('Z') && !str.includes('+') && !str.slice(10).includes('-')) {
    str += 'Z'
  }
  const d = new Date(str)
  if (isNaN(d.getTime())) return 'Just now'
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${time} · ${day}-${month}-${year}`
}

export default function ChatBubble({ message, onSpeak }) {
  const isUser = message.role === 'user'

  // Formatter for markdown-like bold text (*text* or **text**)
  const formatContent = (text) => {
    if (!text) return ''
    const parts = text.split(/(\*\*.*?\*\*)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-cyan-200">{part.slice(2, -2)}</strong>
      }
      return part
    })
  }

  return (
    <div className={`flex w-full mb-4 animate-fadeIn ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-2xl gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
            isUser
              ? 'bg-gradient-to-tr from-cyan-500 to-blue-600 text-white'
              : 'bg-gradient-to-tr from-teal-500 to-emerald-600 text-slate-950 font-bold'
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Bubble Body */}
        <div className="flex flex-col space-y-1.5">
          {/* Tool Invocation Badges */}
          {!isUser && message.tools_called && message.tools_called.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 mb-0.5">
              {message.tools_called.map((tool, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-cyan-950/80 border border-cyan-500/30 text-[10px] font-mono text-cyan-300 shadow-sm"
                >
                  <Zap className="w-2.5 h-2.5 text-cyan-400" />
                  {tool}
                </span>
              ))}
            </div>
          )}

          {/* Bubble Box */}
          <div
            className={`p-4 rounded-2xl text-sm leading-relaxed shadow-lg relative group ${
              isUser
                ? 'bg-gradient-to-br from-cyan-600 to-blue-700 text-white rounded-tr-sm'
                : 'bg-slate-900/90 border border-slate-800 text-slate-100 rounded-tl-sm backdrop-blur-md'
            }`}
          >
            <div className="whitespace-pre-wrap">{formatContent(message.content)}</div>

            {/* Audio Listen / Replay Button for Assistant */}
            {!isUser && onSpeak && (
              <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between">
                <button
                  onClick={() => onSpeak(message.content, message.language)}
                  className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
                  title="Listen to voice output"
                >
                  <Volume2 className="w-3.5 h-3.5" />
                  <span>Listen / শুনুন / सुनिए</span>
                </button>
              </div>
            )}

            {/* Optional Embedded Weather Card */}
            {message.weatherData && (
              <div className="mt-3">
                <WeatherCard weatherData={message.weatherData} forecastData={message.forecastData} compact={true} />
              </div>
            )}
          </div>

          {/* Timestamp */}
          <span className={`text-[10px] text-slate-500 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {formatMessageTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  )
}
