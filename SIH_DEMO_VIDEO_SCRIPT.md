# WeatherGPT — Screen Recording + Voiceover Script (SIH 2026 Demo Video)

> **Team**: Helix Minds  
> **Problem Statement**: 26068  
> **Target Video Runtime**: ~2.5 to 3.0 minutes  
> **Deliverable Format**: MP4 (1080p, 30fps)

---

## 1. Recommended Recording Tools

| Tool | Why | Cost |
| :--- | :--- | :--- |
| **OBS Studio (Recommended)** | Records screen + mic in one pass, native `.mp4` export, highest fidelity & zero watermarks. | Free & Open Source |
| **Loom (Free Tier)** | Quickest setup, records camera bubble + screen, instant MP4 download. | Free tier |
| **Windows Xbox Game Bar (`Win + G`)** | Built into Windows 11, captures active window directly to `.mp4` (`Videos\Captures`). | Free & Built-in |

### Quick OBS Studio Setup (2 Minutes)
1. **Download & Install**: [obsproject.com](https://obsproject.com/)
2. **Sources**:
   - Click `+` under **Sources** &rarr; **Window Capture** (select your browser) or **Display Capture**.
   - Click `+` under **Sources** &rarr; **Audio Input Capture** &rarr; pick your microphone.
3. **Output Settings**:
   - Go to **Settings** &rarr; **Output** &rarr; Recording Format: `mp4`.
   - Video: Resolution `1920x1080`, Framerate `30 fps`.
4. **10-Second Test**: Do a short test clip to verify mic levels and video smoothness.

---

## 2. Pre-Recording Checklist

- [ ] **Silence Notifications**: Turn on Windows Focus Assist / Do Not Disturb; close WhatsApp, Telegram, Slack, and email clients.
- [ ] **Pre-load Tabs**:
  1. Tab 1: [https://weathergpt12.netlify.app](https://weathergpt12.netlify.app) *(Main App)*
  2. Tab 2: [https://weathergpt-backend-g6ds.onrender.com/docs](https://weathergpt-backend-g6ds.onrender.com/docs) *(FastAPI Swagger Docs proving live backend)*
  3. Tab 3: Disaster Operations Map view inside the app.
- [ ] **Warm Up Render Backend**: Render free tier instances spin down after inactivity. Open the app and trigger a test query **5 minutes prior** so the backend is hot and answers instantly.
- [ ] **Pre-arm Demo Alert**: Have the disaster alert ready to trigger or already populated.
- [ ] **Rehearse Once**: Run through the narration once silently to nail pacing.

---

## 3. Cue-by-Cue Narration & Action Script

### [0:00 – 0:15] — Hook & Introduction
* **Screen Action**: Display WeatherGPT home / chat screen (clean state, nothing clicked yet).
* **Narration**:
  > *"Most weather apps show complicated isobar charts and technical jargon that rural farmers and fisherfolk simply can't act on. This is WeatherGPT — India's conversational meteorological intelligence layer. It speaks native Bengali, Hindi, and English, grounds every answer in live data, and pushes disaster alerts in under a hundred milliseconds. Let me show you how it works."*

---

### [0:15 – 0:45] — Live Conversational Query & Grounded Citing
* **Screen Action**: Type in the query input box:  
  `Will it rain in Kolkata tomorrow evening?`  
  Hit Send. When the response renders, hover over the data source attribution and timestamp at the bottom of the message bubble.
* **Narration**:
  > *"Here's a citizen asking a simple question. Behind the scenes, WeatherGPT isn't guessing — it's calling our live weather API, checking for any active district alerts, and only then generating this answer. Notice it cites the data source and the timestamp right here — that's deliberate. The AI is never allowed to invent a forecast or a warning; it can only report what the live data actually says."*

---

### [0:45 – 1:10] — Persona & Role-Based Decision Intelligence
* **Screen Action**: Switch persona/role selector to **Farmer** (or submit prompt):  
  `I'm a farmer in Nadia — should I irrigate tomorrow?`
* **Narration**:
  > *"Now watch what happens when the same weather event is asked about by a farmer instead of a general citizen. The advice changes — it's not just the raw forecast, it's a practical recommendation: postpone irrigation, here's why, here's the rain probability window. The same underlying data, reasoned differently for each type of user — a farmer, a fisherman, a disaster manager — each gets an answer that's actually useful to them."*

---

### [1:10 – 1:40] — Vernacular Voice Interaction (Hands-Free)
* **Screen Action**: Switch language dropdown to **Bengali (বাংলা)**. Tap the microphone icon, say:  
  `কাল বৃষ্টি হবে?` (Kal brishti hobe?)  
  Wait for speech recognition and the automated Bengali speech synthesis playback.
* **Narration**:
  > *"India's rural population often can't read complex English or Hindi bulletins — so voice and language were core requirements, not an afterthought. I'll switch to Bengali and just ask by voice."*  
  *(Wait 2-3 seconds for audio playback)*  
  > *"It transcribed the question, answered in Bengali, and read the response back out loud — completely hands-free, which matters a lot for a farmer standing in a field with a basic smartphone."*

---

### [1:40 – 2:10] — Real-Time GIS Disaster Operations Map
* **Screen Action**: Switch to the **Disaster Operations Map** tab/view. Trigger or highlight the real-time alert for Nadia district (polygons/markers updating live).
* **Narration**:
  > *"Now the disaster-management side. This is the live risk map — districts are color-coded by alert severity in real time over a WebSocket connection, so there's no manual refresh. Watch — I'm triggering a heavy-rainfall warning for Nadia district right now."*  
  *(Highlight map update animation / banner)*  
  > *"That update reached the map in well under a second. A disaster manager sitting in an operations room sees this the instant it happens, not fifteen minutes later over SMS like a lot of legacy systems."*

---

### [2:10 – 2:35] — Real Architecture & FastAPI Backend Verification
* **Screen Action**: Switch to the browser tab with Swagger UI:  
  `https://weathergpt-backend-g6ds.onrender.com/docs`  
  Briefly scroll through endpoints (`/api/v1/weather`, `/api/v1/chat`, `/api/v1/alerts/ws`).
* **Narration**:
  > *"And to be clear, this isn't a mockup — this is a real, live backend. Here's our FastAPI service with interactive API documentation, running right now on Render, backed by a PostgreSQL and PostGIS database on Supabase. Every response you just saw came from this actual running system."*

---

### [2:35 – 2:55] — Final Impact & Conclusion
* **Screen Action**: Switch back to the main WeatherGPT application homepage.
* **Narration**:
  > *"WeatherGPT turns raw meteorological data into something a citizen, a farmer, a fisherman, or a disaster manager can actually act on — in their own language, by voice, in real time, and always grounded in real data. That's WeatherGPT, built by team Helix Minds for Problem Statement 26068. Thank you."*
* **Screen Action**: Stop Recording.

---

## 4. Post-Recording Polish

1. **Check Video & Audio**: Play back the `.mp4` file with headphones. Verify speech clarity and confirm no private notifications popped up.
2. **Trim Dead Air**: If needed, trim the first 1-2 seconds before speaking and the end after "Thank you".
   - *Command-line shortcut (lossless trim)*:
     ```bash
     ffmpeg -i raw_take.mp4 -ss 00:00:02 -to 00:02:55 -c copy HelixMinds_WeatherGPT_PS26068_Demo.mp4
     ```
3. **Naming Convention**: Save as:
   `HelixMinds_WeatherGPT_PS26068_Demo.mp4`
4. **Cloud Backup**: Upload a backup copy to Google Drive / YouTube (unlisted) in case portal uploads fail on deadline day.

---

## 5. Alternative: Automated Voiceover Generation
If you prefer not to narrate live on mic:
1. Record your screen actions in OBS silently.
2. Generate automated voiceover using Microsoft Edge Neural TTS or ElevenLabs.
3. Merge the generated audio track onto your screen recording using CapCut, DaVinci Resolve, or `ffmpeg`:
   ```bash
   ffmpeg -i screen_recording.mp4 -i voiceover.mp3 -c:v copy -c:a aac -shortest final_demo.mp4
   ```
