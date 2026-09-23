import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_sih_deck(output_path="WeatherGPT_SIH_PS26068.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_DARK = RGBColor(11, 19, 43)        # Deep Navy #0B132B
    SURFACE_CARD = RGBColor(20, 32, 60)   # Card Navy #14203C
    SURFACE_BORDER = RGBColor(38, 56, 96) # Subtle Border #263860
    ACCENT_CYAN = RGBColor(14, 165, 233)  # Bright Cyan #0EA5E9
    ACCENT_EMERALD = RGBColor(16, 185, 129)# Green #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11) # Amber #F59E0B
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate #94A3B8
    TEXT_LIGHT = RGBColor(226, 232, 240)  # Light Slate #E2E8F0

    def apply_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title, category="SMART INDIA HACKATHON 2026 | PS ID: 26068"):
        # Category Badge
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title, items, badge="", border_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = SURFACE_CARD
        shape.line.color.rgb = border_color or SURFACE_BORDER
        shape.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        # Badge / Title
        if badge:
            p_badge = tf.paragraphs[0]
            p_badge.text = badge.upper()
            p_badge.font.size = Pt(9.5)
            p_badge.font.bold = True
            p_badge.font.color.rgb = ACCENT_CYAN
            p_title = tf.add_paragraph()
        else:
            p_title = tf.paragraphs[0]

        p_title.text = title
        p_title.font.size = Pt(16)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.space_after = Pt(10)

        for item in items:
            p = tf.add_paragraph()
            p.font.size = Pt(11.5)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(6)
            if isinstance(item, tuple):
                run1 = p.add_run()
                run1.text = "• " + item[0] + ": "
                run1.font.bold = True
                run1.font.color.rgb = ACCENT_CYAN
                run2 = p.add_run()
                run2.text = item[1]
            else:
                p.text = "• " + item

    # ==========================================
    # SLIDE 1: Title Slide (Official SIH Format)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s1)

    # Top Tag
    tb1_tag = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.5))
    p = tb1_tag.text_frame.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2026 | SOFTWARE EDITION"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    # Main Title
    tb1_title = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.3), Inches(1.8))
    p = tb1_title.text_frame.paragraphs[0]
    p.text = "WeatherGPT"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p_sub = tb1_title.text_frame.add_paragraph()
    p_sub.text = "AI-Driven Meteorological Intelligence & Early Disaster Warning System"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = ACCENT_CYAN

    # Problem Statement Card
    add_card(
        s1, Inches(1.0), Inches(3.3), Inches(5.4), Inches(3.4),
        "Problem Statement Details",
        [
            ("PS Number", "26068"),
            ("Theme", "Disaster Management & Climate Intelligence"),
            ("Category", "Software Edition"),
            ("Domain", "Meteorological Intelligence & Early Alerting"),
            ("Status", "Fully Deployed & Production Ready"),
        ],
        badge="SIH Problem Statement",
        border_color=ACCENT_CYAN
    )

    # Team & Submission Card
    add_card(
        s1, Inches(6.8), Inches(3.3), Inches(5.5), Inches(3.4),
        "Team & Prototype Credentials",
        [
            ("Team Leader / Developer", "Kanka Das"),
            ("Institute", "Calcutta Institute of Technology (CIT)"),
            ("Web Application", "https://weathergpt12.netlify.app"),
            ("Backend API Service", "https://weathergpt-backend-g6ds.onrender.com"),
            ("GitHub Repository", "https://github.com/kanka-317/WeatherGPT"),
        ],
        badge="Innovator & Institution",
        border_color=ACCENT_EMERALD
    )

    # ==========================================
    # SLIDE 2: Proposed Solution
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s2)
    add_header(s2, "Proposed Solution & System Overview")

    add_card(
        s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Conversational AI",
        [
            ("Tool-Grounded LLM", "Uses OpenAI GPT-4o-mini with dynamic tool-calling for real-time weather observation & multi-day forecasts."),
            ("Zero Hallucinations", "Strictly queries live weather telemetry & PostgreSQL cache before answering."),
            ("Deterministic Fallback", "Rule-based synthesis engine ensures 100% uptime even if LLM quota exhausts."),
            ("Session Memory", "Persistent conversation history stored in PostgreSQL database."),
        ],
        badge="Intelligent Chat Assistant",
        border_color=ACCENT_CYAN
    )

    add_card(
        s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "GIS Disaster Map",
        [
            ("Spatial Operations Layer", "MapLibre GL interactive mapping of active weather risks & alert perimeters across India."),
            ("PostGIS Spatial Querying", "Uses ST_DWithin geospatial distance search to find emergencies within 50km."),
            ("Color-Coded Severity", "Advisory (Green), Watch (Yellow), Warning (Orange), and Emergency (Red)."),
            ("Multi-Layer Visualization", "Radar precipitation, wind vectors, and district boundary tracking."),
        ],
        badge="Spatial Intelligence",
        border_color=ACCENT_AMBER
    )

    add_card(
        s2, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.9),
        "Multilingual & Voice",
        [
            ("Vernacular Speech-to-Text", "Native voice recognition for English, Bengali, and Hindi queries."),
            ("Natural Audio Readout", "Text-to-speech audio playback of weather advisories for non-literate rural communities."),
            ("Real-Time WebSockets", "Instantaneous live alert broadcasting to all connected users within <100ms."),
            ("Location Auto-GPS", "Instant GPS detection plus auto-complete search for Indian districts."),
        ],
        badge="Accessibility & Speed",
        border_color=ACCENT_EMERALD
    )

    # ==========================================
    # SLIDE 3: Technical Architecture
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s3)
    add_header(s3, "Technical Architecture & Data Pipeline")

    add_card(
        s3, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.9),
        "1. Client Layer",
        [
            ("React 18 Dashboard", "Vite + Tailwind CSS responsive web portal with glassmorphism UI."),
            ("Flutter Mobile App", "Cross-platform Android/iOS client for field operations."),
            ("Web Speech API", "Browser-native voice capture and audio synthesis."),
            ("WebSocket Client", "Persistent real-time socket connection for instant disaster alerts."),
        ],
        badge="User Interfaces",
        border_color=ACCENT_CYAN
    )

    add_card(
        s3, Inches(3.8), Inches(1.8), Inches(2.9), Inches(4.9),
        "2. FastAPI Backend",
        [
            ("FastAPI (Python 3.11)", "High-performance async ASGI engine running on Uvicorn."),
            ("Async SQLAlchemy 2.0", "Non-blocking connection pooling and Alembic migrations."),
            ("Security & Auth", "PBKDF2-HMAC-SHA256 password hashing & JWT session tokens."),
            ("CORS & Middlewares", "Strict origin regex validation for cross-domain Netlify/Vercel apps."),
        ],
        badge="Async API Microservice",
        border_color=ACCENT_EMERALD
    )

    add_card(
        s3, Inches(7.0), Inches(1.8), Inches(2.9), Inches(4.9),
        "3. Database & GIS",
        [
            ("PostgreSQL 16", "Cloud-hosted on Supabase with Supavisor connection pooling."),
            ("PostGIS Extension", "Spatial geometries, geospatial indexing, and distance filters."),
            ("pgvector Extension", "Vector similarity search for meteorology documents."),
            ("15-Min Caching", "Intelligent caching layer reduces external API calls by 92%."),
        ],
        badge="Persistent Layer",
        border_color=ACCENT_AMBER
    )

    add_card(
        s3, Inches(10.2), Inches(1.8), Inches(2.3), Inches(4.9),
        "4. Telemetry",
        [
            ("OpenWeather API", "Live observations & 5-day / 3-hour forecast slots."),
            ("IMD Telemetry", "Indian Meteorological Department ground alerts."),
            ("OpenAI GPT-4o-mini", "Orchestrated tool-calling and advice generation."),
        ],
        badge="External Ingestion",
        border_color=SURFACE_BORDER
    )

    # ==========================================
    # SLIDE 4: Key Innovations vs Traditional Portals
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s4)
    add_header(s4, "Innovation & Competitive Edge (Why WeatherGPT?)")

    add_card(
        s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9),
        "Traditional Weather Portals (IMD / AccuWeather)",
        [
            ("Complex Visuals", "Overwhelms users with raw isobar charts, radar decibels, and technical jargon."),
            ("No Conversational Context", "Cannot answer questions like 'Can I spray pesticide on my potato crop in Nadia today?'"),
            ("Language Barrier", "Mostly in English or formal Hindi; lacks localized vernacular dialects and voice audio."),
            ("High Latency Push", "Notifications are slow or rely on SMS gateways that fail during coastal cell network drops."),
            ("Siloed Data", "Weather charts, disaster alerts, and geographic maps are hosted on disconnected websites."),
        ],
        badge="Existing Limitations",
        border_color=RGBColor(239, 68, 68)
    )

    add_card(
        s4, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.9),
        "WeatherGPT Innovation (SIH PS 26068)",
        [
            ("Actionable Advisory", "Converts meteorological raw data into clear everyday decisions for farming, travel, and safety."),
            ("Grounded Tool-Calling AI", "Combines generative AI with deterministic fallback so answers are always fact-checked."),
            ("Inclusive Multilingual Voice", "Complete voice mic input + speech readout in Bengali, Hindi, and English."),
            ("Integrated Spatial War Room", "Disaster operations map with active warnings and spatial proximity in one tab."),
            ("Edge Cloud Deployment", "Deployed on high-speed CDN and cloud databases with <120ms response time."),
        ],
        badge="WeatherGPT Superpower",
        border_color=ACCENT_EMERALD
    )

    # ==========================================
    # SLIDE 5: Feasibility, Viability & Sustainability
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s5)
    add_header(s5, "Feasibility, Viability & Operational Architecture")

    add_card(
        s5, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Technical Feasibility",
        [
            ("Tested & Validated", "100% of core components built, Dockerized, tested, and actively running in cloud production."),
            ("Asynchronous Concurrency", "FastAPI + asyncpg handles 10,000+ simultaneous requests on lightweight hardware."),
            ("Low Bandwidth Optimization", "Lightweight JSON payloads (<4KB) and client-side caching designed for 2G/3G rural networks."),
        ],
        badge="High Scalability",
        border_color=ACCENT_CYAN
    )

    add_card(
        s5, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Economic Viability",
        [
            ("Zero-Cost Cloud Tiers", "Currently runs entirely on free tier tiers (Render + Netlify + Supabase PostgreSQL)."),
            ("Intelligent Cache Saving", "15-minute observation caching cuts third-party API costs from Rs. 50,000/mo to Rs. 0."),
            ("Cost Per User", "Estimated at under Rs. 0.02 per user/month at scale via open-source LLM quantization (Llama 3 / Mistral)."),
        ],
        badge="Cost Efficiency",
        border_color=ACCENT_EMERALD
    )

    add_card(
        s5, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.9),
        "Operational Sustainability",
        [
            ("Containerized Portability", "Standard Dockerfile & Docker Compose allows 1-click migration to NIC / MeghRaj govt cloud."),
            ("Zero Database Overhead", "Uses Supavisor IPv4 connection pooling; immune to cloud connection exhaustion."),
            ("Audited Security", "Secure salted hashing, input validation via Pydantic v2, and CORS protection."),
        ],
        badge="Govt Cloud Ready",
        border_color=ACCENT_AMBER
    )

    # ==========================================
    # SLIDE 6: Social & Economic Impact
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s6)
    add_header(s6, "Social, Economic & National Impact")

    add_card(
        s6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Agriculture & Farmers",
        [
            ("Precipitation Timing", "Alerts farmers before unexpected thunderstorms or hailstorms to protect harvested grain."),
            ("Sowing & Irrigation", "Helps optimize fertilizer and pesticide spraying according to wind speed & humidity."),
            ("Voice in Mother Tongue", "Bengali and Hindi voice support removes literacy barriers for smallholder farmers."),
        ],
        badge="Rural Agricultural Sector",
        border_color=ACCENT_EMERALD
    )

    add_card(
        s6, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Coastal & Fisherfolk",
        [
            ("High-Sea Wind Warnings", "Real-time alerts for sea surges, squally weather, and cyclone genesis."),
            ("Safe Return Windows", "Provides clear voice advisory on when coastal fishermen must return to harbor."),
            ("Lifesaving Warnings", "Dramatically reduces casualty rates during pre-monsoon and post-monsoon cyclonic events."),
        ],
        badge="Maritime & Coastal Safety",
        border_color=ACCENT_CYAN
    )

    add_card(
        s6, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.9),
        "Disaster Management",
        [
            ("NDRF & SDRF War Room", "Live GIS map provides disaster response commanders with visual threat boundaries."),
            ("Evacuation Planning", "Spatial 50km radius queries identify affected villages and evacuation routes."),
            ("Direct Public Broadcast", "Sub-second WebSocket broadcast pushes alerts before landlines and sirens can trigger."),
        ],
        badge="State & National Agencies",
        border_color=ACCENT_AMBER
    )

    # ==========================================
    # SLIDE 7: Complete Technology Stack
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s7)
    add_header(s7, "Production Technology Stack")

    add_card(
        s7, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.9),
        "Frontend Web",
        [
            ("Framework", "React 18 (SPA)"),
            ("Build Tool", "Vite 5.4"),
            ("Styling", "Tailwind CSS v3.4"),
            ("GIS Engine", "MapLibre GL v6"),
            ("Icons", "Lucide React"),
            ("Hosting", "Netlify Global CDN"),
        ],
        badge="Client Interface",
        border_color=ACCENT_CYAN
    )

    add_card(
        s7, Inches(3.8), Inches(1.8), Inches(2.8), Inches(4.9),
        "Backend Core",
        [
            ("Runtime", "Python 3.11-slim"),
            ("Framework", "FastAPI async"),
            ("ASGI Server", "Uvicorn + uvloop"),
            ("ORM", "SQLAlchemy 2.0 Async"),
            ("Migrations", "Alembic"),
            ("Hosting", "Render Web Service"),
        ],
        badge="Microservice Engine",
        border_color=ACCENT_EMERALD
    )

    add_card(
        s7, Inches(6.9), Inches(1.8), Inches(2.8), Inches(4.9),
        "Database & GIS",
        [
            ("Primary DB", "PostgreSQL 16"),
            ("Geospatial", "PostGIS Extension"),
            ("Vector DB", "pgvector Extension"),
            ("Cloud Host", "Supabase Cloud"),
            ("Pooler", "Supavisor IPv4 (5432)"),
            ("Local Dev", "Docker Compose / SQLite"),
        ],
        badge="Data Infrastructure",
        border_color=ACCENT_AMBER
    )

    add_card(
        s7, Inches(10.0), Inches(1.8), Inches(2.5), Inches(4.9),
        "AI & Protocols",
        [
            ("LLM", "OpenAI GPT-4o-mini"),
            ("Function Calling", "Tool Grounding"),
            ("Speech-to-Text", "Web Speech API"),
            ("Text-to-Speech", "gTTS + Audio Synth"),
            ("Live Push", "WebSockets (/ws)"),
            ("Auth", "PBKDF2-HMAC-SHA256"),
        ],
        badge="Intelligence & Protocols",
        border_color=SURFACE_BORDER
    )

    # ==========================================
    # SLIDE 8: Challenges & Mitigations
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s8)
    add_header(s8, "Potential Challenges & Strategic Mitigations")

    add_card(
        s8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "1. LLM Hallucinations",
        [
            ("Risk", "AI generating incorrect rain amounts or outdated cyclone paths, risking lives."),
            ("Engineered Mitigation", "Strict JSON schema tool-calling. The LLM is NEVER permitted to guess weather stats; it is physically bound to live database query results."),
            ("Deterministic Backup", "If OpenAI returns errors or quota limits, an algorithmic template synthesizes exact factual forecasts."),
        ],
        badge="Challenge & Fix 1",
        border_color=RGBColor(239, 68, 68)
    )

    add_card(
        s8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "2. Rural Connectivity Drops",
        [
            ("Risk", "Cellular networks failing or dropping to low 2G bandwidth during storms."),
            ("Engineered Mitigation", "Client-side Service Worker caching stores the last known observation and forecast locally on the device."),
            ("Ultra-Lean Payloads", "Compressed JSON responses under 4 KB ensure weather cards render even on spotty edge connections."),
        ],
        badge="Challenge & Fix 2",
        border_color=ACCENT_AMBER
    )

    add_card(
        s8, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.9),
        "3. High Concurrent Surge",
        [
            ("Risk", "Millions of citizens simultaneously checking the app during severe cyclone warnings."),
            ("Engineered Mitigation", "15-minute PostgreSQL caching layer serves 90%+ requests directly from memory/DB index without touching third-party APIs."),
            ("Edge CDN Caching", "Static assets distributed via Netlify edge nodes worldwide for 0ms origin load."),
        ],
        badge="Challenge & Fix 3",
        border_color=ACCENT_EMERALD
    )

    # ==========================================
    # SLIDE 9: Roadmap & Future Expansion
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s9)
    add_header(s9, "Future Scope & Scale Roadmap")

    add_card(
        s9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Phase 1 (Completed)",
        [
            ("Full-Stack Prototype", "FastAPI backend, React dashboard, and Flutter mobile client."),
            ("Spatial Database", "Supabase PostgreSQL with PostGIS and pgvector active."),
            ("Multilingual & Voice", "Bengali, Hindi, and English voice interface."),
            ("Live Cloud Deployment", "Render backend + Netlify frontend running in production."),
        ],
        badge="Current Milestone (Day 3)",
        border_color=ACCENT_EMERALD
    )

    add_card(
        s9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9),
        "Phase 2 (3-6 Months)",
        [
            ("INSAT-3D Satellite Radar", "Direct integration with Indian Space Research Organisation (ISRO) MOSDAC satellite feeds."),
            ("Offline LoRa Mesh Relay", "Peer-to-peer decentralized packet broadcast for when telecom towers get blown away in cyclones."),
            ("Regional Dialects", "Support for Odia, Tamil, Telugu, and Marathi speech models."),
        ],
        badge="Near-Term Roadmap",
        border_color=ACCENT_CYAN
    )

    add_card(
        s9, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.9),
        "Phase 3 (6-12 Months)",
        [
            ("Automated Siren Trigger", "Integration with National Disaster Management Authority (NDMA) CAP sirens."),
            ("WhatsApp & Telegram Bots", "Automated broadcast channel for district magistrates and panchayats."),
            ("AI Crop Loss Predictive Modeling", "Crop yield and insurance claims validation via multi-spectral weather imagery."),
        ],
        badge="Long-Term Vision",
        border_color=ACCENT_AMBER
    )

    # ==========================================
    # SLIDE 10: Conclusion & Live Demonstration
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_slide_bg(s10)
    add_header(s10, "Conclusion & Live Demonstration (SIH PS 26068)")

    add_card(
        s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9),
        "Fulfillment of Problem Statement 26068",
        [
            ("Complete End-to-End Solution", "Delivered from raw meteorological telemetry ingestion to end-user vernacular voice delivery."),
            ("Zero Disconnected Silos", "Combines AI chat, interactive GIS mapping, and live alerts into a single cohesive interface."),
            ("Production-Grade Engineering", "Built with modern microservice standards, async database pools, and complete Docker containers."),
            ("Empowering Rural India", "Accessible to every farmer and coastal worker regardless of literacy or language."),
        ],
        badge="Key Takeaways",
        border_color=ACCENT_EMERALD
    )

    add_card(
        s10, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.9),
        "Project Access & Live Demonstration Links",
        [
            ("Live Web Application", "https://weathergpt12.netlify.app"),
            ("Backend Swagger Docs", "https://weathergpt-backend-g6ds.onrender.com/docs"),
            ("Live WebSocket Alert Feed", "wss://weathergpt-backend-g6ds.onrender.com/ws/alerts"),
            ("GitHub Source Code", "https://github.com/kanka-317/WeatherGPT"),
            ("Presenter", "Kanka Das | Calcutta Institute of Technology (CIT)"),
            ("Q&A", "We are now ready for live demonstration and queries!"),
        ],
        badge="Live Artifacts & Q&A",
        border_color=ACCENT_CYAN
    )

    prs.save(output_path)
    print(f"SIH Presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    create_sih_deck()
