import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from src.pipeline import run_decision
from src.data_models.model import Scenario


st.set_page_config(
    page_title = "NETRA",
    page_icon = "🚨",
    layout = "wide",
)
st.title("NETRA")
st.subheader("Network Emergency Triage & Response Assistant")
st.write("Decision intelligence for prioritising telecom restoration during disasters")

st.divider()

flood_level = st.slider("flood level (m)", min_value=0.0, max_value=5.0, value=2.0, step=0.5)

if st.button("Run Scenario"):
    scenario = Scenario(id = f'flood_{flood_level}m', flood_level=flood_level, road_access_multiplier=max(0.0, 1.0-flood_level*0.05))

    result = run_decision(scenario)
    st.subheader("Scenario Result")
    st.json(result)


