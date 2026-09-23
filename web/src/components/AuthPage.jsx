import React, { useState } from 'react'
import {
  CloudLightning,
  Lock,
  Mail,
  User,
  Shield,
  Languages,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  Check,
  X,
  KeyRound,
} from 'lucide-react'

// Default seed users for SIH demo testing
const DEFAULT_REGISTERED_USERS = [
  {
    name: 'Animesh Roy (Farmer)',
    email: 'citizen@weathergpt.gov.in',
    password: 'Password123!',
    role: 'citizen',
    language: 'bn',
  },
  {
    name: 'SDMA Ops Director',
    email: 'disaster_officer@weathergpt.gov.in',
    password: 'Password123!',
    role: 'disaster_officer',
    language: 'en',
  },
  {
    name: 'Debjit Das',
    email: 'debjit@weathergpt.gov.in',
    password: 'Password123!',
    role: 'citizen',
    language: 'en',
  },
]

function getRegisteredUsers() {
  try {
    const raw = localStorage.getItem('weathergpt_registered_users')
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    }
  } catch {}
  localStorage.setItem('weathergpt_registered_users', JSON.stringify(DEFAULT_REGISTERED_USERS))
  return DEFAULT_REGISTERED_USERS
}

function saveRegisteredUser(newUser) {
  const users = getRegisteredUsers()
  const filtered = users.filter((u) => u.email.toLowerCase() !== newUser.email.toLowerCase())
  filtered.push(newUser)
  localStorage.setItem('weathergpt_registered_users', JSON.stringify(filtered))
}

export default function AuthPage({ onLogin, backendUrl = 'http://localhost:8000' }) {
  const [mode, setMode] = useState('signin') // 'signin' | 'signup'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [role, setRole] = useState('citizen') // 'citizen' | 'disaster_officer' | 'researcher'
  const [preferredLang, setPreferredLang] = useState('en')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  // Validation Rules
  const isValidEmail = (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)
  const isMinLength = password.length >= 8
  const hasUpper = /[A-Z]/.test(password)
  const hasLower = /[a-z]/.test(password)
  const hasNumber = /[0-9]/.test(password)
  const hasSpecial = /[^A-Za-z0-9]/.test(password)
  const passwordsMatch = confirmPassword.length > 0 && password === confirmPassword
  const passwordsMismatch = confirmPassword.length > 0 && password !== confirmPassword

  // Password Strength Calculation (0 to 4)
  const strengthScore = [
    isMinLength,
    hasUpper && hasLower,
    hasNumber,
    hasSpecial,
  ].filter(Boolean).length

  const getStrengthInfo = () => {
    if (!password) return { label: 'Enter a strong password', color: 'text-slate-500', bar: 'bg-slate-700' }
    if (strengthScore <= 1) return { label: 'Weak', color: 'text-rose-400', bar: 'bg-rose-500' }
    if (strengthScore === 2) return { label: 'Fair', color: 'text-amber-400', bar: 'bg-amber-500' }
    if (strengthScore === 3) return { label: 'Good', color: 'text-cyan-400', bar: 'bg-cyan-500' }
    return { label: 'Strong', color: 'text-emerald-400', bar: 'bg-emerald-500' }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    // Common Email Validation
    if (!email.trim()) {
      setError('Please enter your email address.')
      return
    }
    if (!isValidEmail(email.trim())) {
      setError('Please enter a valid email format (e.g. user@example.com).')
      return
    }

    const registeredUsers = getRegisteredUsers()

    // Sign In Password Validation & Existing Account Check
    if (mode === 'signin') {
      if (!password) {
        setError('Please enter your password.')
        return
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters.')
        return
      }

      setIsLoading(true)

      // 1. Try real database authentication via PostgreSQL API
      try {
        const resp = await fetch(`${backendUrl}/auth/signin`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email.trim().toLowerCase(),
            password: password,
          }),
        })

        if (resp.ok) {
          const data = await resp.json()
          const user = {
            id: data.id,
            name: data.name,
            email: data.email,
            role: data.role || 'citizen',
            language: data.preferred_language || 'en',
            token: data.token,
          }
          localStorage.setItem('weathergpt_user', JSON.stringify(user))
          setIsLoading(false)
          onLogin(user)
          return
        }

        if (resp.status === 404) {
          setError('No account found with this email. Please check your email or click "Create Account".')
          setIsLoading(false)
          return
        } else if (resp.status === 401) {
          setError('Password does not match. Please verify your password and try again.')
          setIsLoading(false)
          return
        }
      } catch (err) {
        console.warn('PostgreSQL backend auth unreachable, checking offline store:', err)
      }

      // 2. Offline / local fallback check
      const existingUser = registeredUsers.find(
        (u) => u.email.toLowerCase() === email.trim().toLowerCase()
      )

      if (!existingUser) {
        setError('No account found with this email. Please check your email or click "Create Account".')
        setIsLoading(false)
        return
      }

      if (existingUser.password && existingUser.password !== password) {
        setError('Password does not match. Please verify your password and try again.')
        setIsLoading(false)
        return
      }

      const user = {
        name: existingUser.name,
        email: existingUser.email,
        role: existingUser.role || 'citizen',
        language: existingUser.language || 'en',
        token: 'auth-user-token-' + Math.random().toString(36).substring(2, 10),
      }
      localStorage.setItem('weathergpt_user', JSON.stringify(user))
      setIsLoading(false)
      onLogin(user)
      return
    }

    // Sign Up Password & Profile Validation
    if (mode === 'signup') {
      if (!name.trim()) {
        setError('Please enter your full name.')
        return
      }

      if (!isMinLength) {
        setError('Password must be at least 8 characters long.')
        return
      }
      if (!hasUpper || !hasLower) {
        setError('Password must contain both uppercase and lowercase letters.')
        return
      }
      if (!hasNumber && !hasSpecial) {
        setError('Password must contain at least one number or special character.')
        return
      }
      if (!passwordsMatch) {
        setError('Passwords do not match. Please ensure both password fields are identical.')
        return
      }

      setIsLoading(true)

      // 1. Try real database registration via PostgreSQL API
      try {
        const resp = await fetch(`${backendUrl}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name.trim(),
            email: email.trim().toLowerCase(),
            password: password,
            role: role,
            preferred_language: preferredLang,
          }),
        })

        if (resp.ok) {
          const data = await resp.json()
          const newUser = {
            id: data.id,
            name: data.name,
            email: data.email,
            role: data.role || 'citizen',
            language: data.preferred_language || 'en',
            token: data.token,
          }
          saveRegisteredUser({ ...newUser, password })
          localStorage.setItem('weathergpt_user', JSON.stringify(newUser))
          setIsLoading(false)
          onLogin(newUser)
          return
        }

        if (resp.status === 409) {
          setError('An account with this email already exists. Please switch to Sign In.')
          setIsLoading(false)
          return
        }
      } catch (err) {
        console.warn('PostgreSQL backend signup unreachable, saving locally:', err)
      }

      // 2. Offline fallback registration
      const emailExists = registeredUsers.some(
        (u) => u.email.toLowerCase() === email.trim().toLowerCase()
      )
      if (emailExists) {
        setError('An account with this email already exists. Please switch to Sign In.')
        setIsLoading(false)
        return
      }

      const newUser = {
        name: name.trim(),
        email: email.trim(),
        password: password,
        role: role,
        language: preferredLang,
        token: 'auth-user-token-' + Math.random().toString(36).substring(2, 10),
      }
      saveRegisteredUser(newUser)
      localStorage.setItem('weathergpt_user', JSON.stringify(newUser))
      setIsLoading(false)
      onLogin(newUser)
    }
  }

  // Fast Demo 1-Click Login for SIH Presentation
  const handleQuickDemoLogin = async (selectedRole, defaultName, defaultLang) => {
    const defaultEmail = `${selectedRole}@weathergpt.gov.in`
    try {
      const resp = await fetch(`${backendUrl}/auth/signin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: defaultEmail,
          password: 'Password123!',
        }),
      })
      if (resp.ok) {
        const data = await resp.json()
        const user = {
          id: data.id,
          name: data.name,
          email: data.email,
          role: data.role,
          language: data.preferred_language || defaultLang,
          token: data.token,
        }
        localStorage.setItem('weathergpt_user', JSON.stringify(user))
        onLogin(user)
        return
      }
    } catch {}

    const user = {
      name: defaultName,
      email: defaultEmail,
      role: selectedRole,
      language: defaultLang,
      token: 'demo-token-' + Math.random().toString(36).substring(2, 10),
    }
    localStorage.setItem('weathergpt_user', JSON.stringify(user))
    onLogin(user)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden selection:bg-cyan-500 selection:text-slate-950">
      {/* Background Animated Gradient Mesh */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 left-1/4 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Auth Container */}
      <div className="w-full max-w-md relative z-10">
        {/* Branding Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-xl shadow-cyan-500/30 text-white mb-3 ring-4 ring-cyan-500/10">
            <CloudLightning className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center justify-center gap-2">
            <span>WeatherGPT</span>
            <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-semibold">
              SIH PS 26068
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            AI Meteorological Intelligence & Disaster Early-Warning System
          </p>
        </div>

        {/* Card Box */}
        <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800/80 shadow-2xl backdrop-blur-2xl">
          {/* Toggle Sign In / Sign Up Tabs */}
          <div className="flex rounded-xl bg-slate-950/80 border border-slate-800/80 p-1 mb-5">
            <button
              type="button"
              onClick={() => {
                setMode('signin')
                setError(null)
                setConfirmPassword('')
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                mode === 'signin'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('signup')
                setError(null)
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                mode === 'signup'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2 animate-fadeIn">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {/* Full Name for Sign Up */}
            {mode === 'signup' && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                <div className="relative flex items-center">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Debjit Das"
                    className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
                  />
                </div>
              </div>
            )}

            {/* Email Address */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative flex items-center">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (error) setError(null)
                  }}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-medium text-slate-300">
                  {mode === 'signup' ? 'Create Password' : 'Password'}
                </label>
                {mode === 'signup' && password.length > 0 && (
                  <span className={`text-[11px] font-semibold ${getStrengthInfo().color}`}>
                    {getStrengthInfo().label}
                  </span>
                )}
              </div>
              <div className="relative flex items-center">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (error) setError(null)
                  }}
                  placeholder={mode === 'signup' ? 'Minimum 8 characters' : 'Enter your password'}
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-slate-400 hover:text-slate-200 transition-colors focus:outline-none"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Sign In Mode Password Helper */}
              {mode === 'signin' && (
                <div className="mt-1.5 flex items-center justify-between text-[11px]">
                  {password.length > 0 && password.length < 6 ? (
                    <span className="text-amber-400 flex items-center gap-1">
                      <span>⚠️ Minimum 6 characters required ({password.length}/6)</span>
                    </span>
                  ) : password.length >= 6 ? (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <Check className="w-3 h-3" />
                      <span>Password format valid</span>
                    </span>
                  ) : (
                    <span className="text-slate-500">Minimum 6 characters</span>
                  )}
                </div>
              )}

              {/* Sign Up Mode: Real-time Strength Meter & Validation Checklist */}
              {mode === 'signup' && (
                <div className="mt-2 space-y-2">
                  {/* Strength Meter Bars */}
                  <div className="grid grid-cols-4 gap-1.5 h-1.5 w-full bg-slate-950/80 rounded-full p-0.5 border border-slate-800/80 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        strengthScore >= 1 ? getStrengthInfo().bar : 'bg-transparent'
                      }`}
                    />
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        strengthScore >= 2 ? getStrengthInfo().bar : 'bg-transparent'
                      }`}
                    />
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        strengthScore >= 3 ? getStrengthInfo().bar : 'bg-transparent'
                      }`}
                    />
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        strengthScore >= 4 ? getStrengthInfo().bar : 'bg-transparent'
                      }`}
                    />
                  </div>

                  {/* Requirements Live Checklist */}
                  <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px]">
                    <div
                      className={`flex items-center gap-1.5 transition-colors ${
                        isMinLength ? 'text-emerald-400 font-medium' : 'text-slate-500'
                      }`}
                    >
                      {isMinLength ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : (
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-600 ml-1 mr-1" />
                      )}
                      <span>8+ characters</span>
                    </div>

                    <div
                      className={`flex items-center gap-1.5 transition-colors ${
                        hasUpper && hasLower ? 'text-emerald-400 font-medium' : 'text-slate-500'
                      }`}
                    >
                      {hasUpper && hasLower ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : (
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-600 ml-1 mr-1" />
                      )}
                      <span>Upper & lower case</span>
                    </div>

                    <div
                      className={`flex items-center gap-1.5 transition-colors ${
                        hasNumber || hasSpecial ? 'text-emerald-400 font-medium' : 'text-slate-500'
                      }`}
                    >
                      {hasNumber || hasSpecial ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : (
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-600 ml-1 mr-1" />
                      )}
                      <span>Number or symbol</span>
                    </div>

                    <div
                      className={`flex items-center gap-1.5 transition-colors ${
                        passwordsMatch ? 'text-emerald-400 font-medium' : 'text-slate-500'
                      }`}
                    >
                      {passwordsMatch ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : (
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-600 ml-1 mr-1" />
                      )}
                      <span>Passwords match</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password Field for Sign Up */}
            {mode === 'signup' && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-medium text-slate-300">Confirm Password</label>
                  {confirmPassword.length > 0 && (
                    <span
                      className={`text-[11px] font-semibold flex items-center gap-1 ${
                        passwordsMatch ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {passwordsMatch ? (
                        <>
                          <Check className="w-3 h-3" />
                          <span>Matched</span>
                        </>
                      ) : (
                        <>
                          <X className="w-3 h-3" />
                          <span>Does not match</span>
                        </>
                      )}
                    </span>
                  )}
                </div>
                <div className="relative flex items-center">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <KeyRound className="w-4 h-4" />
                  </div>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value)
                      if (error) setError(null)
                    }}
                    placeholder="Re-enter your password"
                    className={`w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950/60 border text-slate-100 placeholder-slate-500 text-xs focus:outline-none transition-all ${
                      confirmPassword.length > 0
                        ? passwordsMatch
                          ? 'border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30'
                          : 'border-rose-500/60 focus:ring-1 focus:ring-rose-500/30'
                        : 'border-slate-800 focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30'
                    }`}
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="text-slate-400 hover:text-slate-200 transition-colors focus:outline-none"
                    >
                      {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Role & Language for Sign Up */}
            {mode === 'signup' && (
              <div className="grid grid-cols-2 gap-2.5 pt-1">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Your Role</label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-2.5 py-2 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500/60"
                  >
                    <option value="citizen">Farmer / Citizen</option>
                    <option value="disaster_officer">Disaster Officer</option>
                    <option value="researcher">Scientist / Analyst</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Language</label>
                  <select
                    value={preferredLang}
                    onChange={(e) => setPreferredLang(e.target.value)}
                    className="w-full px-2.5 py-2 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500/60"
                  >
                    <option value="en">English (EN)</option>
                    <option value="bn">বাংলা (Bengali)</option>
                    <option value="hi">हिन्दी (Hindi)</option>
                  </select>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold tracking-wide transition-all shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2 group disabled:opacity-50"
            >
              <span>{mode === 'signin' ? 'Sign In to Dashboard' : 'Complete Registration'}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </form>

          {/* Quick Demo Logins for Judges */}
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>SIH Presentation 1-Click Fast Login:</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemoLogin('citizen', 'Animesh Roy (Farmer)', 'bn')}
                className="p-2 rounded-xl bg-slate-950 hover:bg-slate-850 border border-slate-800 hover:border-cyan-500/40 text-left transition-all group"
              >
                <div className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300">
                  👨‍🌾 Citizen / Farmer
                </div>
                <div className="text-[10px] text-slate-400 font-light">Bengal Farmer (বাংলা)</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemoLogin('disaster_officer', 'SDMA Ops Director', 'en')}
                className="p-2 rounded-xl bg-slate-950 hover:bg-slate-850 border border-slate-800 hover:border-orange-500/40 text-left transition-all group"
              >
                <div className="text-xs font-semibold text-slate-200 group-hover:text-orange-300">
                  🛡️ Disaster Officer
                </div>
                <div className="text-[10px] text-slate-400 font-light">State Emergency Team</div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-4 text-center text-[11px] text-slate-500 font-light">
          Built for Smart India Hackathon 2024 · Ministry & State Disaster Authority Stack
        </div>
      </div>
    </div>
  )
}
