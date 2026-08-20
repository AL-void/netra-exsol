# NETRA - Network Emergency Triage & Response Assistant
*Built for the Exasol AI Build Challenge 2026*

## ?? Overview
During severe climate events and natural disasters, telecommunication failures isolate critical infrastructure. Conventional restoration models prioritize cell towers based on raw subscriber counts, often leaving emergency lifeline facilities (such as trauma hospitals, flood shelters, and fire stations) disconnected.

**NETRA** is an AI-powered decision-intelligence and triage system that models dynamic flood progression, network topology, facility dependencies, and zero-redundancy risks to calculate a **Societal Impact Index (SII)** for optimal tower restoration and emergency crew dispatch.

---

## ? Role of Exasol Personal
Exasol Personal serves as the high-performance, in-memory analytical backbone for NETRA:
- **In-Memory Graph & Spatial Joins:** Executes sub-second joins across cell tower coverage footprints, critical facilities, and real-time crew positions.
- **Dynamic Simulation Pushdown:** Pushes dynamic flood-elevation thresholds directly into in-memory SQL execution layers to recalculate network failure states instantaneously.
- **Redundancy Analysis:** Evaluates real-time primary and secondary link matrices to flag facilities facing total communication blackouts.

---

## ??? Architecture & Tech Stack
- **Database Engine:** Exasol Personal Edition (Docker Local)
- **Data Access Layer:** `pyexasol` (Python WebSocket connector with SSL handling)
- **Decision Engine:** Societal Impact Index (SII) scoring and nearest-crew routing optimization
- **Command Dashboard:** Streamlit & Folium

---

## ?? Quickstart & Deployment Guide (Exasol Personal Local)

Follow these steps to run the complete NETRA system locally:

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Installed and running)
- Python 3.10+

---

### 2. Launch Exasol Personal Container
Run the official Exasol Docker container.

> **Important:** The `--privileged` flag is required so Exasol can manage internal Linux system daemons without crash loops on Docker Desktop.

```bash
docker run --name exasol_netra -p 8563:8563 --privileged -d exasol/docker-db:latest
```

*Wait 30-45 seconds for Exasol to fully initialize its in-memory database engine.*

---

### 3. Install Dependencies
Clone this repository and install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### 4. Initialize Database Schema & Synthetic Data
Execute the setup script to create the `NETRA` schema, build the tables, and load the realistic Bengaluru crisis dataset:

```bash
python setup_database.py
```

*Expected output:*
```text
Connected to Exasol successfully!
Tables created successfully.
All sample data successfully loaded into Exasol Personal!
```

---

### 5. Launch the Command Dashboard
Start the interactive Streamlit disaster management console:

```bash
streamlit run src/dashboard/app.py
```

Open your browser and navigate to:
```text
http://localhost:8501
```

---

## ?? Video Demo & Pitch Deck
- **3-Minute Demo Video:** [Link to Demo Video](https://your-video-link-here)
- **Pitch Deck (PDF):** Available in [`docs/pitch_deck.pdf`](docs/pitch_deck.pdf)

---

## ?? Team
- **Abhishek Kartik**
- **Sudeepa**
- **AL-void**
