import React from 'react'
import { Sparkles, Sprout, CloudRain, ShieldAlert } from 'lucide-react'

const PROMPTS = {
  en: [
    {
      icon: <CloudRain className="w-4 h-4 text-cyan-400 shrink-0" />,
      label: 'Forecast Rain (Exit Check)',
      query: 'Will it rain in Kolkata tomorrow?',
    },
    {
      icon: <Sprout className="w-4 h-4 text-emerald-400 shrink-0" />,
      label: 'Farmer Irrigation Advisory',
      query: 'Should I irrigate my crops in Nadia tomorrow?',
    },
    {
      icon: <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />,
      label: 'Active Weather Warnings',
      query: 'Are there any active weather warnings or alerts for Kolkata?',
    },
    {
      icon: <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />,
      label: 'Current Conditions',
      query: 'What is the current weather and wind speed in Delhi?',
    },
  ],
  bn: [
    {
      icon: <CloudRain className="w-4 h-4 text-cyan-400 shrink-0" />,
      label: 'বৃষ্টির পূর্বাভাস (Exit Check)',
      query: 'কাল বৃষ্টি হবে?',
    },
    {
      icon: <Sprout className="w-4 h-4 text-emerald-400 shrink-0" />,
      label: 'কৃষক সেচ পরামর্শ',
      query: 'কাল কি নদীয়াতে সেচ দেওয়া উচিত?',
    },
    {
      icon: <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />,
      label: 'সক্রিয় দুর্যোগ সতর্কতা',
      query: 'কলকাতায় কি কোনো বজ্রঝড়ের সতর্কতা আছে?',
    },
    {
      icon: <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />,
      label: 'বর্তমান আবহাওয়া',
      query: 'কলকাতার বর্তমান তাপমাত্রা এবং আবহাওয়া কেমন?',
    },
  ],
  hi: [
    {
      icon: <CloudRain className="w-4 h-4 text-cyan-400 shrink-0" />,
      label: 'बारिश का पूर्वानुमान (Exit Check)',
      query: 'कल बारिश होगी?',
    },
    {
      icon: <Sprout className="w-4 h-4 text-emerald-400 shrink-0" />,
      label: 'किसान सिंचाई सलाह',
      query: 'क्या मुझे कल नादिया में फसलों में सिंचाई करनी चाहिए?',
    },
    {
      icon: <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />,
      label: 'मौसम चेतावनी',
      query: 'क्या कोलकाता में कोई आंधी या तूफान की चेतावनी है?',
    },
    {
      icon: <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />,
      label: 'वर्तमान मौसम',
      query: 'दिल्ली का वर्तमान मौसम और तापमान क्या है?',
    },
  ],
}

export default function SuggestedPrompts({ onSelectPrompt, language = 'en' }) {
  const currentPrompts = PROMPTS[language] || PROMPTS.en
  return (
    <div className="w-full my-3">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2 px-1 flex items-center gap-1.5">
        <Sparkles className="w-3 h-3 text-cyan-400" />
        <span>Suggested Demo Queries:</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {currentPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(p.query)}
            className="p-3 rounded-xl bg-slate-900/60 hover:bg-slate-850 border border-slate-800 hover:border-cyan-500/40 text-left transition-all duration-200 group flex items-start gap-2.5 shadow-sm hover:shadow-cyan-950/20"
          >
            <div className="p-1.5 rounded-lg bg-slate-800/80 group-hover:bg-cyan-950/50 group-hover:text-cyan-300 transition-colors">
              {p.icon}
            </div>
            <div>
              <div className="text-xs font-medium text-slate-200 group-hover:text-cyan-300 transition-colors">
                {p.label}
              </div>
              <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5 font-light">
                "{p.query}"
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
