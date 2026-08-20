# NETRA — Network Emergency Triage & Response Assistant
*Built for the Exasol AI Build Challenge 2026*

## 📌 Overview
During severe climate events and disasters, telecommunication failures isolate critical infrastructure. Standard restoration heuristics prioritize towers by sheer user count, leaving emergency facilities stranded. 

**NETRA** is an AI decision-intelligence platform that combines telecom network topology, facility dependencies, elevation data, and dynamic flood modeling to triage tower restoration based on **Societal Impact**, not just population volume.

---

## ⚡ Role of Exasol Personal
Exasol Personal acts as the core high-performance, in-memory analytical engine:
- **In-Memory Graph & Spatial Joins:** Executes millisecond joins between cell coverage radii and lifeline facilities (trauma centers, emergency shelters, fire hubs).
- **Dynamic Simulation Pushdown:** Pushes dynamic flood-level thresholds directly into SQL queries to instantaneously recompute network state.
- **Redundancy Analysis:** Evaluates live fallback connectivity to identify zero-redundancy facilities facing complete communication blackouts.

---

## 🛠️ Architecture & Tech Stack
- **Database Engine:** Exasol Personal Edition (Docker Local)
- **Data Access Layer:** `pyexasol` (Python WebSocket connector)
- **Decision Engine:** Custom Societal Impact Index (SII) scoring & crew proximity optimization
- **Command Dashboard:** Streamlit & Folium

---

## 🚀 Quickstart & Deployment Guide (Exasol Personal Local)

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Running)
- Python 3.10+

### 2. Start Exasol Personal Container
```bash
docker run --name exasol_netra -p 8563:8563 -d exasol/docker-db:latest