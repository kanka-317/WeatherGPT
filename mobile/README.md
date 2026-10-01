# WeatherGPT Mobile Client (Flutter)

A cross-platform mobile client for **WeatherGPT** (SIH PS 26068), built with **100% feature parity** with the live web dashboard ([weathergpt12.netlify.app](https://weathergpt12.netlify.app)), connected to the production cloud backend at `https://weathergpt-backend-g6ds.onrender.com`.

---

## 📱 Full Module Architecture

```text
mobile/
├── pubspec.yaml
└── lib/
    ├── main.dart                             # App entry, glassmorphic dark theme, bottom navigation shell
    ├── core/
    │   ├── constants.dart                    # Backend URLs, WebSocket endpoints, color tokens, personas
    │   └── storage.dart                      # SharedPreferences local persistence (sessions, chat, role)
    ├── models/
    │   ├── weather_models.dart               # Current weather, 5-day forecast, atmospheric telemetry
    │   ├── alert_model.dart                  # Active alerts, color-coded severity, icons
    │   ├── chat_message.dart                 # Chat bubbles, explainability metadata, tools called
    │   └── user_model.dart                   # Role-based user profile (Citizen, Farmer, Fisherman, Admin)
    ├── services/
    │   ├── api_service.dart                  # Centralized HTTP client with Render cold-start retry
    │   └── websocket_service.dart            # Live /ws/alerts subscription with auto-reconnection
    ├── widgets/
    │   ├── weather_summary_card.dart         # Glassmorphic telemetry & swipeable forecast card
    │   ├── chat_bubble_widget.dart           # Chat bubble with "Why this answer" explainability
    │   ├── alert_banner_widget.dart          # Live in-app push alert banner
    │   ├── role_selector_sheet.dart          # Persona switcher modal (Citizen, Farmer, Fisherman, War Room)
    │   └── waking_server_indicator.dart      # Render free-tier cold-start indicator banner
    └── screens/
        ├── chat_screen.dart                  # 1. Conversational Chat + Voice + Explainability
        ├── real_time_weather_screen.dart     # 2. Comprehensive real-time weather & 5-day forecast
        ├── alerts_screen.dart                # 3. Early Warning & Live Alert Feed (WebSockets)
        ├── risk_map_screen.dart              # 6. GIS Disaster Risk Map (flutter_map)
        ├── climate_analytics_screen.dart     # 7. Climate Trends & Forecast Analytics (fl_chart)
        ├── disaster_manager_screen.dart      # 8. Disaster Manager Dashboard (Admin War Room)
        └── auth_screen.dart                  # 9. Sign In / Sign Up & Persona Management
```

---

## 🎨 Intentional Mobile UI Adaptations

| Module | Web Dashboard Layout | Mobile App Adaptation | Rationale |
| :--- | :--- | :--- | :--- |
| **Disaster Manager Dashboard** | Wide multi-column data table | **Card list + KPI chips** | Tables with 6+ columns cause severe horizontal scrolling on phones. Card list preserves all severity badges, timestamps, and dismiss actions natively. |
| **Forecast Intervals** | Wide horizontal timeline | **Swipeable cards + 2-tab view** | Splits into *"Current & Hourly"* and *"5-Day Forecast"* tabs for ergonomic vertical scrolling. |
| **GIS Risk Map** | WebGL canvas with overlay sidebar | **Full-screen map + Bottom sheet modal** | Tapping district pins slides up an interactive bottom sheet war room rather than squishing a desktop sidebar onto a 6-inch display. |
| **Role Selector** | Top bar dropdown menu | **Modal bottom sheet** | Thumb-friendly bottom sheet with descriptive persona badges and role descriptions. |

---

## 🚀 Building & Running

### 1. Install Dependencies
```bash
flutter pub get
```

### 2. Run Locally (Emulator / Physical Device)
```bash
flutter run
```

### 3. Build Production APK (Free Distribution for Judges)
```bash
flutter build apk --release
```
The output APK will be located at:
`build/app/outputs/flutter-apk/app-release.apk`
