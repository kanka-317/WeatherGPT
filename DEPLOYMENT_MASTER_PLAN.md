# WeatherGPT — Full Free Deployment Master Plan
### End-to-End Free-Tier Production Infrastructure Runbook (SIH 2026 • Problem Statement 26068)

> **Team**: Helix Minds  
> **Philosophy**: Zero infrastructure costs, 100% cloud resilience, zero cold-starts during judging.  
> **Execution Order**: Database (Supabase) &rarr; Backend (Render) &rarr; Web Dashboard (Netlify/Vercel) &rarr; Mobile (GitHub Releases & Flutter Web) &rarr; Reliability (Sentry & Uptime Heartbeat).

---

## 🗺️ Architectural Flow & Dependencies

```mermaid
graph TD
    A[Step 1: Supabase Free Tier<br>PostGIS + pgvector] -->|DATABASE_URL| B[Step 2: Render FastAPI Web Service<br>Dockerized Python 3.11]
    B -->|REST API + WebSockets| C[Step 3: Web Dashboard<br>Netlify / Vercel]
    B -->|REST API + WebSockets| D[Step 4a: Android APK<br>Hosted on GitHub Releases]
    B -->|REST API + WebSockets| E[Step 4b: Flutter Web Fallback<br>Zero-install browser app]
    F[Step 5: cron-job.org / UptimeRobot<br>10-min /health ping] -->|Keeps Alive| B
    B -->|Captures unhandled errors| G[Step 5: Sentry Free Tier<br>Real-time exception logging]
```

---

## STEP 1 — Database (Supabase Free Tier)

Supabase provides a free, hosted PostgreSQL database with 500 MB storage and native support for extensions.

### 1. Create Supabase Project
1. Log into [supabase.com](https://supabase.com) and click **New project**.
2. **Project Name**: `weathergpt-db`
3. **Database Password**: Generate and copy a strong password. Save this securely.
4. **Region**: Choose `South Asia (Mumbai) - ap-south-1` (or `Singapore - ap-southeast-1`) for lowest latency to Indian meteorological endpoints.
5. Select the **Free Tier** and click **Create new project** (takes ~60 seconds to provision).

### 2. Enable PostGIS & pgvector via SQL Editor
1. In the Supabase left sidebar, click **SQL Editor**.
2. Click **New query** and paste the following snippet:
   ```sql
   -- Enable PostGIS for geospatial queries & district boundary matching
   CREATE EXTENSION IF NOT EXISTS postgis;

   -- Enable pgvector for LLM embeddings & RAG similarity search
   CREATE EXTENSION IF NOT EXISTS vector;

   -- Verify extensions are active
   SELECT * FROM pg_extension WHERE extname IN ('postgis', 'vector');
   ```
3. Click **Run**. Confirm both extensions return with status installed.

### 3. Extract the Supavisor Pooler Connection String
To ensure seamless IPv4 compatibility with cloud providers (like Render and local development), use Supabase's connection pooler:
1. In Supabase, go to **Project Settings** &rarr; **Database** &rarr; scroll to **Connection string**.
2. Select the **URI** tab and choose **Mode: Session** (Port `5432`).
3. The raw URI looks like:
   ```text
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
   ```
4. **Driver Prefix**: In WeatherGPT, our engine automatically normalizes `postgresql://` and `postgres://` into `postgresql+asyncpg://` and strips query params like `sslmode` to ensure `asyncpg` operates smoothly.
5. Save this URI — this is your `DATABASE_URL` for Step 2.

### 4. Run Alembic Migrations
From your local terminal, apply the database schema against Supabase:
```powershell
cd "d:\Weather Gpt\backend"
# Set your Supabase connection string:
$env:DATABASE_URL="postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

# Execute migrations:
python -m alembic upgrade head
```
*Expected Output*:
```text
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_enable_postgis_pgvector
INFO  [alembic.runtime.migration] Running upgrade 0001_enable_postgis_pgvector -> 0002_add_weather_models
INFO  [alembic.runtime.migration] Running upgrade 0002_add_weather_models -> 0003_add_chat_models
```
*Verification*: Check Supabase **Table Editor** &rarr; confirm tables `weather_records`, `forecast_records`, `district_alerts`, `chat_sessions`, and `chat_messages` are created.

---

## STEP 2 — Backend (FastAPI on Render Free Tier)

Render provides 750 free compute hours/month for Web Services running Docker.

### 1. Verify Production Docker Configuration
The repository includes a production-ready [`backend/Dockerfile`](backend/Dockerfile):
- Base image: `python:3.11-slim` with system C-libraries (`libpq-dev`, `build-essential`).
- Runs automated database schema checks upon launch.
- Starts `uvicorn` with dynamic `${PORT:-8000}`.
- Resource-optimized to stay within Render's 512 MB memory boundary.

### 2. Create Render Web Service
1. Log into [render.com](https://dashboard.render.com).
2. Click **New +** &rarr; **Web Service**.
3. Connect your GitHub repository (`Weather-GPT` / `WeatherGPT`).
4. Configure service settings:
   - **Name**: `weathergpt-backend`
   - **Region**: `Oregon (US West)` or closest available.
   - **Branch**: `main`
   - **Root Directory**: *(leave blank)*
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Instance Type**: `Free` (0.1 CPU, 512 MB RAM)

### 3. Set Environment Variables on Render
In the Render service **Environment** tab, add:

| Key | Example Value / Source | Notes |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `WeatherGPT` | App title |
| `DEBUG` | `False` | Production mode |
| `DATABASE_URL` | `postgresql+asyncpg://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:5432/postgres` | From Step 1 |
| `JWT_SECRET` | *(Click "Generate" or 32+ random hex characters)* | Auth encryption key |
| `CORS_ORIGINS` | `*` | Or specify frontend URLs |
| `OPENAI_API_KEY` | `sk-proj-...` | For conversational RAG & persona reasoning |
| `OPENWEATHER_API_KEY` | `...` | For live meteorological data ingestion |
| `SENTRY_DSN` | *(Optional - from Step 5)* | Error tracking |

### 4. WebSocket Support Verification on Render
- **Status**: **Fully Supported**. Render natively supports HTTP/1.1 WebSockets on all plans, including Free tier.
- **Render Idle Behavior**:
  - Render free instances spin down after **15 minutes** of no HTTP requests.
  - Active WebSocket connections hold an idle timeout of **100 seconds** if no data or ping frame travels across the wire.
  - **Mitigation**: WeatherGPT includes WebSocket ping heartbeats, and Step 5 sets up an external 10-minute HTTP ping to ensure the server never sleeps.

### 5. Verify Live Backend
Once Render builds and reports `Live`:
1. **Health Check**: Open `https://<your-render-subdomain>.onrender.com/health` &rarr; should return `{"status":"ok"}`.
2. **Swagger Documentation**: Open `https://<your-render-subdomain>.onrender.com/docs` &rarr; verify interactive endpoints load cleanly.
3. Save your backend URL: e.g. `https://weathergpt-backend-g6ds.onrender.com`.

---

## STEP 3 — Web Dashboard (React on Netlify or Vercel Free Tier)

Deploy the web frontend with continuous deployment and automatic SSL.

### Option A: Netlify (Recommended — Already configured in [`netlify.toml`](netlify.toml))
1. Log into [netlify.com](https://app.netlify.com).
2. Click **Add new site** &rarr; **Import an existing project** &rarr; select GitHub repository.
3. Build Settings (auto-detected from root `netlify.toml`):
   - **Base directory**: `web`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
4. In **Environment variables**, set:
   - `VITE_API_URL` = `https://<your-render-backend-url>.onrender.com`
   - `VITE_WS_URL` = `wss://<your-render-backend-url>.onrender.com/ws/alerts`
5. Click **Deploy weathergpt-web**.
6. Set custom domain or use default: e.g. `https://weathergpt12.netlify.app`.

### Option B: Vercel
1. Log into [vercel.com](https://vercel.com) &rarr; **Add New...** &rarr; **Project**.
2. Select repository, set **Root Directory** to `web`.
3. Add environment variable `VITE_API_URL` pointing to your Render backend.
4. Click **Deploy**.

### Verify Web Dashboard
1. Open the deployed website URL.
2. In the chat interface, send a test prompt: *"What is the weather in Kolkata?"*
3. Switch to the **Disaster Operations Map** &rarr; check browser DevTools console to confirm WebSocket connected:
   ```text
   [WebSocket] Connected to wss://.../ws/alerts
   ```

---

## STEP 4 — Mobile (Flutter Client Free Distribution)

Deploy the mobile application without paying $25 for a Google Play Console account.

### 1. Build Signed Android APK
If Flutter is installed locally:
```bash
cd "d:\Weather Gpt\mobile"
flutter pub get
flutter build apk --release --dart-define=BACKEND_URL=https://<your-render-subdomain>.onrender.com
```
The compiled standalone APK is generated at:
`mobile/build/app/outputs/flutter-apk/app-release.apk`

### 2. Host APK via GitHub Releases (Direct Free Sideloading)
1. In your GitHub repository, click **Releases** &rarr; **Draft a new release**.
2. Tag: `v1.0.0`
3. Release title: `WeatherGPT Mobile v1.0.0 (SIH PS 26068)`
4. Drag and drop `app-release.apk` (renamed to `WeatherGPT_PS26068_v1.0.0.apk`).
5. Click **Publish release**. Evaluators can download and install directly on any Android smartphone.

### 3. Deploy Zero-Install Flutter Web Fallback
For evaluators with iPhones, Macs, or desktops:
```bash
flutter build web --release --dart-define=BACKEND_URL=https://<your-render-subdomain>.onrender.com
```
Deploy the generated `mobile/build/web/` folder directly to Netlify or Vercel as a second site:
e.g. `https://weathergpt-mobile-web.netlify.app`.

### 4. Automated Cloud CI/CD (No Local Flutter Installation Required!)
We have created [`.github/workflows/mobile_release.yml`](.github/workflows/mobile_release.yml).
- Go to GitHub &rarr; **Actions** &rarr; **Build & Release Mobile App (APK & Web)** &rarr; **Run workflow**.
- Provide your Render backend URL.
- GitHub's cloud runners build both the APK and Web fallback, and publish the release automatically.

---

## STEP 5 — Monitoring & Reliability (Zero Cold Starts)

### 1. Sentry Free Tier Error Tracking
1. Create a free account at [sentry.io](https://sentry.io).
2. Create project &rarr; Platform: **Python (FastAPI)**.
3. Copy your Client Key DSN: `https://[KEY]@[HOST]/[PROJECT_ID]`.
4. In Render Dashboard &rarr; `weathergpt-backend` &rarr; **Environment** &rarr; add:
   `SENTRY_DSN = https://...`
5. Save changes. WeatherGPT will automatically initialize Sentry on startup. Any unhandled API exception or AI timeout will immediately log to your Sentry dashboard during evaluation.

### 2. Automated 10-Minute Uptime Keep-Alive (Defeating Render Cold Starts)
Render's free tier suspends inactive containers after 15 minutes. To guarantee **0-second response times** for judges:
1. Go to [cron-job.org](https://cron-job.org) (100% free forever) or [uptimerobot.com](https://uptimerobot.com).
2. Click **Create Cronjob**:
   - **Title**: `WeatherGPT Render KeepAlive`
   - **URL**: `https://<your-render-subdomain>.onrender.com/health`
   - **Schedule**: **Every 10 minutes** (`*/10 * * * *`)
   - **Request Method**: `GET`
3. Save and enable the job.
4. Render will receive a `/health` ping every 10 minutes, keeping the container warm 24/7.

---

## STEP 6 — Deployment Handoff & Single Source of Truth

### 📋 Live URLs Registry

| Component | Target Platform | Live URL / Endpoint |
| :--- | :--- | :--- |
| **Supabase Dashboard** | Supabase Cloud | `https://supabase.com/dashboard/project/<PROJECT_REF>` |
| **PostgreSQL Pooler** | Supavisor (Port 5432) | `aws-0-<region>.pooler.supabase.com:5432/postgres` |
| **FastAPI Backend Root** | Render Web Service | `https://<your-service>.onrender.com` |
| **FastAPI Health Check** | Render Web Service | `https://<your-service>.onrender.com/health` |
| **Interactive API Docs** | Render Web Service | `https://<your-service>.onrender.com/docs` |
| **WebSocket Alerts** | Render Web Service | `wss://<your-service>.onrender.com/ws/alerts` |
| **Web Dashboard** | Netlify / Vercel | `https://weathergpt12.netlify.app` |
| **Mobile APK Download** | GitHub Releases | `https://github.com/<USER>/<REPO>/releases/tag/v1.0.0` |
| **Flutter Web Fallback** | Netlify / Vercel | `https://weathergpt-mobile-web.netlify.app` |
| **Error Monitoring** | Sentry Dashboard | `https://sentry.io/organizations/<ORG>/issues/` |
| **Uptime Monitor** | cron-job.org | Active (`GET /health` every 10m) |

---

### 🔑 Environment Variables Master Inventory

#### 1. Backend (`Render.com` Web Service)
```ini
PROJECT_NAME="WeatherGPT"
DEBUG="False"
DATABASE_URL="postgresql+asyncpg://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:5432/postgres"
JWT_SECRET="[32_CHARACTER_HEX_STRING]"
CORS_ORIGINS="*"
OPENAI_API_KEY="sk-proj-..."
OPENWEATHER_API_KEY="[YOUR_OPENWEATHER_KEY]"
SENTRY_DSN="https://[KEY]@[HOST]/[PROJECT_ID]"
```

#### 2. Web Frontend (`Netlify` / `Vercel`)
```ini
VITE_API_URL="https://<your-render-backend>.onrender.com"
VITE_WS_URL="wss://<your-render-backend>.onrender.com/ws/alerts"
```

#### 3. Mobile Build (`Flutter` CLI / GitHub Actions)
```ini
BACKEND_URL="https://<your-render-backend>.onrender.com"
```

---

## 💡 Emergency Troubleshooting & Recovery

- **Problem: Database connection timeout from Render**  
  *Fix*: Ensure you are using the **Pooler URL** (`aws-0-[region].pooler.supabase.com:5432`), not the direct database connection (`db.[ref].supabase.co`). Render's free tier operates over IPv4; direct Supabase endpoints require IPv6 or Supavisor pooler.
- **Problem: CORS errors in browser console**  
  *Fix*: Backend `app/main.py` is configured with `allow_origin_regex=r"^https?://.*"` which permits all origins. Verify `VITE_API_URL` does not have a trailing slash.
- **Problem: Render app takes 45 seconds to respond**  
  *Fix*: Your keep-alive cron job was paused or not configured. Set up the 10-minute ping on [cron-job.org](https://cron-job.org) to keep the container memory active.
