# trackbuddyy.
TrackBuddy is an intelligent travel planning platform that helps users explore unfamiliar cities without wasting time, exceeding their budget, struggling with overcrowded tourist attractions, or making complicated transport and accommodation decisions.  
# TrackBuddy — Smart Travel Planning & Optimization Platform
> **Tagline:** Explore More. Spend Smarter. Travel Together.  
> **Theme:** Vintage Heritage Edition (Earthy Terracotta, Sandstone Ochre, Forest Sage, Aged Paper Parchment — strictly avoiding AI blue)  
> **Primary Hub:** Jaipur, Rajasthan (Extensible architecture for pan-India and international hubs)

---

## 🌟 Executive Overview & Six Questions Answered

TrackBuddy combines itinerary generation, multi-modal transport comparisons, budget engineering, weather-aware scheduling, hostel recommendations, and group debt settlement into one cohesive platform.

1. **Where should I go?** — Curated heritage monuments, havelis, museums, and bazaars with opening hours and admission rates.
2. **What is the best order to visit the places?** — Geometric nearest-neighbor heuristic with 2-opt route refinement that avoids crisscrossing city traffic.
3. **How should I travel between them?** — Direct comparison table of Walking, Auto-Rickshaw, App Taxis (Uber/Ola), Metro, and Local Buses.
4. **How much will the complete trip cost?** — Deterministic backend expense engine calculating exact group totals and per-person allocations.
5. **Where should I stay?** — Vetted student-friendly hostels, heritage havelis, and budget stays with transparent occupancy indicators.
6. **What should I change if plans become impractical?** — Automated crowd-avoidance recommendations and weather-adaptive rescheduling.

---

## 🚀 Quick Start & Setup

### 1. Requirements
- Python 3.9+ (Tested on Python 3.15)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Installation
```powershell
# Navigate into the project folder
cd C:\Users\Vinayak\.gemini\antigravity\scratch\trackbuddy

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```powershell
python database/seed.py
```

### 4. Run the Application
```powershell
python app.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 🧪 Running Automated Tests

Run the complete test suite:
```powershell
pytest tests/test_core.py -v
```
All 9 core test suites pass:
- Haversine distance verification
- Deterministic budget calculations
- Group expense debt settlement matrix
- Itinerary generation and student concession application
- Multi-modal transport comparison
- Student discount catalog integrity
- Grounded AI fallback execution
- Flask health check and API endpoints

---

## 🏆 Official Hackathon Demonstration Scenario

**Scenario:** 4 college students (Aarav, Neha, Kabir, Riya) planning a 2-day trip to Jaipur with a group budget of ₹6,000.

1. **One-Click Preset:** On the homepage or `/planner`, click **"Load Jaipur Hackathon Demo"**.
2. **Itinerary & Route Map (`/itinerary`):**
   - Inspect Day 1 and Day 2 stops plotted on the Leaflet OpenStreetMap.
   - See visit windows, arrival/departure times, and transit legs.
   - Reorder stops using ▲/▼ buttons and click **"Re-optimize Stops"**.
   - Trigger the **"Peak Crowd Advisory"** alternative action.
3. **Transport Comparison (`/transport`):**
   - Compare fares and travel times for 4 passengers between Railway Station and Amber Fort across Auto, Cab, Metro, and Walking.
4. **Hotels Catalog (`/hotels`):**
   - Filter by hostels (Zostel, Moustache) and inspect demo occupancy indicators (e.g., *Moderate occupancy*, *Nearly full*).
5. **Student Discounts (`/discounts`):**
   - Review verified Rajasthan Archaeology concessions (up to 75% off ticket counters with bona fide college ID).
6. **Weather Dashboard (`/weather`):**
   - Live meteorological data from Open-Meteo with scheduling impact advice.
7. **Expense Calculator & Group Split (`/expenses`):**
   - Deterministic calculations: ~₹5,420 total estimated expenditure (~₹1,355 per person), leaving a ₹580 surplus under the ₹6,000 budget!
   - Record shared bills (e.g. dinner, autos) and view exact debt settlements (who owes whom).
8. **AI Assistant (`/assistant`):**
   - Chat with the companion; answers are strictly grounded in verified facts with no fabricated prices or fake discounts.

---

## ⚙️ Configuration & API Key Transparency

TrackBuddy is engineered to be fully usable out-of-the-box with **zero mandatory API keys**:

| Service | Provider Configured | API Key Required? | Status / Fallback Behavior |
| :--- | :--- | :---: | :--- |
| **Mapping & Routing** | OpenStreetMap + OSRM | No | Live OSRM routing with geometric Haversine fallback |
| **Weather** | Open-Meteo | No | Live Open-Meteo forecast with demo meteorological fallback |
| **Local AI** | Ollama (`gemma2:2b`) | No (Local) | Live Ollama when server is running; intelligent deterministic grounded engine when offline |
| **Transit & Fares** | Regional Transport Tariffs | No | Verified JMRC and RTA fare tables |
| **Accommodations** | Curated Seed DB | Optional | Clearly attributed demo listings with occupancy indicators |

To customize providers, copy `.env.example` to `.env` and configure:
- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `gemma2:2b`)
- `WEATHER_PROVIDER` (`open-meteo`)
- `ROUTING_PROVIDER` (`osrm`)
