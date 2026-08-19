import pyexasol
import ssl

# 1. Connect to Exasol
C = pyexasol.connect(
    dsn='localhost:8563',
    user='sys',
    password='exasol',
    encryption=True,
    websocket_sslopt={'cert_reqs': ssl.CERT_NONE}
)

print("Connected to Exasol...")
C.execute("CREATE SCHEMA IF NOT EXISTS NETRA;")
C.execute("OPEN SCHEMA NETRA;")

# 2. Re-create base tables
C.execute("""
CREATE OR REPLACE TABLE cell_towers (
    tower_id VARCHAR(10) PRIMARY KEY,
    tower_name VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    elevation_meters DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'ACTIVE'
);
""")

C.execute("""
CREATE OR REPLACE TABLE critical_facilities (
    facility_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    facility_type VARCHAR(30),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    lifeline_weight INT
);
""")

C.execute("""
CREATE OR REPLACE TABLE facility_connectivity (
    facility_id VARCHAR(10),
    tower_id VARCHAR(10),
    is_primary_link BOOLEAN,
    PRIMARY KEY (facility_id, tower_id)
);
""")

C.execute("""
CREATE OR REPLACE TABLE repair_crews (
    crew_id VARCHAR(10) PRIMARY KEY,
    crew_name VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    equipment_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'AVAILABLE'
);
""")

# 3. Insert realistic Bengaluru dataset
towers = [
    ('T1', 'Indiranagar 100ft Rd', 12.9784, 77.6408, 3.2, 'FAILED'),
    ('T2', 'Old Airport Rd (Hospital Zone)', 12.9600, 77.6480, 0.8, 'FAILED'),
    ('T3', 'Domlur Flyover Backup', 12.9609, 77.6387, 1.5, 'ACTIVE'),
    ('T4', 'Koramangala 4th Block', 12.9352, 77.6245, 0.5, 'FAILED'),
    ('T5', 'MG Road Metro Station', 12.9756, 77.6066, 4.0, 'ACTIVE'),
    ('T6', 'HSR Layout Sector 1', 12.9121, 77.6446, 1.1, 'FAILED'),
    ('T7', 'Whitefield IT Corridor', 12.9698, 77.7500, 2.8, 'ACTIVE'),
    ('T8', 'Electronic City Phase 1', 12.8452, 77.6602, 1.9, 'ACTIVE')
]
C.import_from_iterable(towers, 'cell_towers')

facilities = [
    ('F1', 'Manipal Hospital (ICU/Trauma)', 'HOSPITAL', 12.9592, 77.6475, 50),
    ('F2', 'Domlur Flood Relief Shelter', 'SHELTER', 12.9615, 77.6350, 30),
    ('F3', 'Koramangala Fire Station', 'FIRE_STATION', 12.9340, 77.6200, 40),
    ('F4', 'Bowring Civil Hospital', 'HOSPITAL', 12.9830, 77.6030, 50),
    ('F5', 'HSR Community Center Shelter', 'SHELTER', 12.9100, 77.6410, 30),
    ('F6', 'Sakra World Hospital', 'HOSPITAL', 12.9280, 77.6830, 50)
]
C.import_from_iterable(facilities, 'critical_facilities')

connectivity = [
    ('F1', 'T2', True),   # Manipal Hospital primarily uses T2
    ('F1', 'T3', False),  # Secondary backup link
    ('F2', 'T3', True),
    ('F3', 'T4', True),   # Fire station only has T4 (single point of failure)
    ('F4', 'T5', True),
    ('F5', 'T6', True),
    ('F6', 'T7', True)
]
C.import_from_iterable(connectivity, 'facility_connectivity')

crews = [
    ('C1', 'Alpha Rapid Response', 12.9716, 77.5946, 'GENERATOR_CREW', 'AVAILABLE'),
    ('C2', 'Bravo Boat Rescue Team', 12.9300, 77.6100, 'BOAT_UNIT', 'AVAILABLE'),
    ('C3', 'Delta Fiber Repair Unit', 12.9800, 77.7000, 'FIBER_CREW', 'AVAILABLE')
]
C.import_from_iterable(crews, 'repair_crews')

# 4. In-Memory Exasol View (Calculates Triage Metrics Inside Database)
C.execute("""
CREATE OR REPLACE VIEW v_tower_impact_summary AS
SELECT 
    t.tower_id,
    t.tower_name,
    t.latitude,
    t.longitude,
    t.elevation_meters,
    t.status,
    COUNT(f.facility_id) AS total_connected_facilities,
    COALESCE(SUM(f.lifeline_weight), 0) AS total_lifeline_weight,
    SUM(CASE WHEN fc.is_primary_link = TRUE THEN 1 ELSE 0 END) AS primary_dependent_facilities
FROM cell_towers t
LEFT JOIN facility_connectivity fc ON t.tower_id = fc.tower_id
LEFT JOIN critical_facilities f ON fc.facility_id = f.facility_id
GROUP BY 
    t.tower_id, t.tower_name, t.latitude, t.longitude, 
    t.elevation_meters, t.status;
""")

print("Database and In-Memory Analytics View successfully updated in Exasol!")
C.close()