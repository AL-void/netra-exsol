import pyexasol
import ssl
import pandas as pd

def get_exasol_connection():
    try:
        return pyexasol.connect(
            dsn='localhost:8563',
            user='sys',
            password='exasol',
            schema='NETRA',
            encryption=False
        )
    except Exception:
        return pyexasol.connect(
            dsn='localhost:8563',
            user='sys',
            password='exasol',
            schema='NETRA',
            encryption=True,
            websocket_sslopt={'cert_reqs': ssl.CERT_NONE}
        )

def fetch_failed_towers_and_facilities():
    """Returns broken towers joined with affected facilities."""
    conn = get_exasol_connection()
    query = """
    SELECT 
        t.tower_id,
        t.tower_name,
        t.latitude AS tower_lat,
        t.longitude AS tower_lon,
        t.elevation_meters,
        f.facility_id,
        f.name AS facility_name,
        f.facility_type,
        f.lifeline_weight,
        fc.is_primary_link
    FROM cell_towers t
    LEFT JOIN facility_connectivity fc ON t.tower_id = fc.tower_id
    LEFT JOIN critical_facilities f ON fc.facility_id = f.facility_id
    WHERE t.status = 'FAILED'
    """
    df = conn.export_to_pandas(query)
    conn.close()
    return df

def fetch_repair_crews():
    """Returns all repair crews and their current availability."""
    conn = get_exasol_connection()
    df = conn.export_to_pandas("SELECT * FROM repair_crews WHERE status = 'AVAILABLE'")
    conn.close()
    return df

def simulate_flood_impact(flood_level_meters: float):
    """
    Simulates dynamic tower failure based on flood water height.
    Towers below or at water level flip to 'FAILED'.
    """
    conn = get_exasol_connection()
    query = f"""
    SELECT 
        tower_id,
        tower_name,
        latitude,
        longitude,
        elevation_meters,
        
        CASE 
            WHEN elevation_meters <= {flood_level_meters} THEN 'FAILED'
            ELSE status 
        END AS dynamic_status
    FROM cell_towers
    """
    df = conn.export_to_pandas(query)
    conn.close()
    return df
if __name__ == "__main__":
    df = fetch_failed_towers_and_facilities()
    print("\n--- Live Data Extracted from Exasol ---")
    print(df)