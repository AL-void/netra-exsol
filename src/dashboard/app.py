import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from src.pipeline import run_decision
from src.data_models.model import Scenario
from db_helper import simulate_flood_impact

import folium
from streamlit_folium import st_folium


st.set_page_config(
    page_title="NETRA",
    page_icon="🚨",
    layout="wide",
)


if "result" not in st.session_state:
    st.session_state.result = None

if "active_flood_level" not in st.session_state:
    st.session_state.active_flood_level = 0.0

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False


def update_flood_level():
    st.session_state.active_flood_level = st.session_state.flood_slider


st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            max-width: 1400px;
        }

        h1 {
            margin-bottom: 0.2rem;
        }

        h2, h3 {
            margin-top: 0.6rem;
            margin-bottom: 0.4rem;
        }

        .stDivider {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        div[data-testid="stMetric"] {
            padding: 0.3rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("NETRA")

st.subheader("Network Emergency Triage & Response Assistant")

st.write(
    "Decision intelligence for prioritising telecom restoration during disasters"
)


if st.session_state.get("analysis_complete", False):
    st.success(
        "✅ AI analysis complete — please scroll down to view the results."
    )


flood_level = st.session_state.active_flood_level


try:
    dynamic_towers = simulate_flood_impact(flood_level)
    database_ok = True
except Exception as e:
    dynamic_towers = None
    database_ok = False
    st.warning(f"Network database unavailable: {e}")


col_map, col_control = st.columns([2.2, 1])


with col_map:

    st.subheader("🗺️ Network Status Map")

    network_map = folium.Map(
        location=[12.975, 77.59],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 9999;
        background: rgba(15, 17, 23, 0.92);
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #444;
        color: white;
        font-size: 14px;
    ">
        <b>Network Status</b><br>
        <span style="color:#2ecc40;">●</span> Active<br>
        <span style="color:#ff4040;">●</span> Failed
    </div>
    """

    network_map.get_root().html.add_child(
        folium.Element(legend_html)
    )

    if database_ok and dynamic_towers is not None:

        for _, tower in dynamic_towers.iterrows():

            tower_id = tower["TOWER_ID"]
            tower_name = tower["TOWER_NAME"]

            latitude = tower["LATITUDE"]
            longitude = tower["LONGITUDE"]

            elevation = tower["ELEVATION_METERS"]
            status = tower["DYNAMIC_STATUS"]

            if status == "FAILED":
                marker_color = "red"
                status_icon = "⚠️"
            else:
                marker_color = "green"
                status_icon = "✓"

            popup_text = f"""
            <div style="font-size: 14px;">
                <b>{status_icon} Tower {tower_id}</b><br>
                <b>Name:</b> {tower_name}<br>
                <b>Status:</b> {status}<br>
                <b>Elevation:</b> {elevation} m<br>
                <b>Flood Level:</b> {flood_level:.1f} m
            </div>
            """

            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(
                    popup_text,
                    max_width=300,
                ),
                tooltip=f"{tower_id} — {status}",
                icon=folium.Icon(
                    color=marker_color,
                    icon="tower",
                    prefix="fa",
                ),
            ).add_to(network_map)

    st_folium(
        network_map,
        width=None,
        height=500,
        key="netra_map",
        returned_objects=[],
    )


with col_control:

    st.subheader("🌊 Flood Scenario")

    new_flood_level = st.slider(
        "Flood level (m)",
        min_value=0.0,
        max_value=5.0,
        value=st.session_state.active_flood_level,
        step=0.5,
        key="flood_slider",
        on_change=update_flood_level,
    )

    st.info(
        f"🌊 **Live Flood Simulation:** "
        f"{st.session_state.active_flood_level:.1f} m"
    )

    st.write("")

    if st.button(
        "🤖 AI Analysis",
        key="run_scenario",
        use_container_width=True,
    ):

        scenario = Scenario(
            id=f"flood_{flood_level}m",
            flood_level=flood_level,
            road_access_multiplier=max(
                0.0,
                1.0 - flood_level * 0.05,
            ),
        )

        st.session_state.result = run_decision(scenario)
        st.session_state.analysis_complete = True

        st.rerun()


if st.session_state.result is not None:

    result = st.session_state.result

    st.divider()

    st.subheader("Restoration Command Center")

    recommendation = result["recommendation"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Priority Tower",
            recommendation["tower_id"],
        )

    with col2:
        st.metric(
            "Impact Score",
            recommendation["priority_score"],
        )

    with col3:
        st.metric(
            "Population Reconnected",
            f'{recommendation["population_reconnected"]:,}',
        )

    with col4:
        st.metric(
            "Critical Facilities",
            recommendation["critical_facilities_reconnected"],
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            f"Restore Tower {recommendation['tower_id']} First"
        )

        st.write(
            f"**Assigned Crew:** "
            f"{recommendation['assigned_crew_id']}"
        )

        st.write(
            f"**Estimated Restoration:** "
            f"{recommendation['estimated_restoration_time']} mins"
        )

    with col2:

        st.subheader("Why NETRA chose this tower")

        st.write(
            recommendation["justification"]
        )

    st.divider()

    st.subheader("Restoration Triage")

    impact_scores = result["raw_summary"]["impact_scores"]

    for tower_id, score in sorted(
        impact_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        st.write(
            f"🔴 **{tower_id}** — "
            f"Impact Score: **{score:.2f}**"
        )