import pyexasol
import pandas as pd
import ssl

def get_exasol_connection():
    return pyexasol.connect(
        dsn="localhost:8563",
        user="sys",
        password="exasol",
        schema="NETRA",
        encryption=True,
        websocket_sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False},
    )

def fetch_failed_towers_and_facilities():
    """Returns failed towers joined with their affected critical facilities."""
    conn = get_exasol_connection()
    query = """
    SELECT
        t.tower_id,
        t.tower_name,
        t.latitude AS tower_lat,
        t.longitude AS tower_lon,
        t.coverage_radius_km,
        t.elevation_meters,
        t.battery_backup_hours,
        f.facility_id,
        f.name AS facility_name,
        f.facility_type,
        f.lifeline_weight,
        fc.is_primary_link
    FROM cell_towers t
    LEFT JOIN facility_connectivity fc
        ON t.tower_id = fc.tower_id
    LEFT JOIN critical_facilities f
        ON fc.facility_id = f.facility_id
    WHERE t.status = 'FAILED'
    """
    try:
        return conn.export_to_pandas(query)
    finally:
        conn.close()

def fetch_repair_crews():
    """Returns all currently available repair crews."""
    conn = get_exasol_connection()
    query = """
    SELECT *
    FROM repair_crews
    WHERE status = 'AVAILABLE'
    """
    try:
        return conn.export_to_pandas(query)
    finally:
        conn.close()

def simulate_flood_impact(flood_level_meters: float):
    """
    Dynamically calculates tower status based on flood level.
    A tower fails when its elevation is <= flood level.
    """
    conn = get_exasol_connection()
    flood_level = float(flood_level_meters)
    query = f"""
    SELECT
        tower_id,
        tower_name,
        latitude,
        longitude,
        coverage_radius_km,
        elevation_meters,
        battery_backup_hours,
        CASE
            WHEN elevation_meters <= {flood_level}
                THEN 'FAILED'
            ELSE status
        END AS dynamic_status
    FROM cell_towers
    ORDER BY tower_id
    """
    try:
        return conn.export_to_pandas(query)
    finally:
        conn.close()