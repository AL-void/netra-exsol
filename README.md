# NETRA - Decision Intelligence for Disaster Response
*Neural Emergency Tower Restoration Algorithm*

License: MIT | Python 3.10+ | Database: Exasol Personal Local

## ?? Quick Links
- **GitHub Repo:** https://github.com/AL-void/netra-exsol
- **Demo Video (3 min):** [Watch Live Walkthrough Video](https://youtu.be/your_actual_video_id)
- **Pitch Deck (PDF):** Available in [\`docs/pitch_deck.pdf\`](docs/pitch_deck.pdf)

---

## ?? Overview
NETRA is an AI-powered decision intelligence engine that optimizes telecom tower restoration during severe climate events and disasters. It answers one critical question:

> **"Which tower should we restore first to save the most lives?"**

Traditional disaster response sends crews to the closest or easiest towers based on raw population count. NETRA sends them to the most impactful towers - considering critical facilities (hospitals, shelters, fire hubs), cascading zero-redundancy failures, and dynamic flood levels.

---

## ? Role of Exasol Personal
Exasol Personal serves as the in-memory analytical backbone:
- **In-Memory Graph & Spatial Joins:** Millisecond joins across cell tower coverage footprints and critical facility dependencies.
- **Dynamic Simulation Pushdown:** Pushes dynamic flood-level thresholds directly into SQL queries to instantaneously recalculate failure states.
- **Redundancy Analysis:** Evaluates real-time link matrices to identify zero-redundancy facilities facing total communication blackouts.

---

## ??? Tech Stack
- **Database Engine:** Exasol Personal Edition (Docker Local)
- **Data Access Layer:** \`pyexasol\` (WebSocket connector with SSL handling)
- **Decision Engine:** NetworkX, SciPy (Optimization), Pydantic, NumPy
- **Command Center UI:** Streamlit & Folium

---

## ?? Quickstart & Deployment Guide (Exasol Personal Local)

### 1. Prerequisites
- Docker Desktop (Running)
- Python 3.10+

### 2. Start Exasol Personal Container
```bash
docker run --name exasol_netra -p 8563:8563 --privileged -d exasol/docker-db:latest
```
*Wait 30-45 seconds for Exasol to fully initialize.*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database Schema & Load Bengaluru Dataset
```bash
python setup_database.py
```

### 5. Launch the Crisis Command Dashboard
```bash
streamlit run src/dashboard/app.py
```
Open \`http://localhost:8501\` in your browser.

---

## ?? Team
- **Abhishek Yadav** - Data Integration & ML Pipeline
- **Abhishek Karthik** - Data Pipeline & System Architecture
- **Sudeepa Priyadarshini** - Impact Modeling & Analytics
