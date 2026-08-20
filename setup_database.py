import pyexasol
import ssl

# 1. Establish connection to Exasol Personal Local
C = pyexasol.connect(
    dsn='localhost:8563',
    user='sys',
    password='exasol',
    encryption=True,
    websocket_sslopt={'cert_reqs': ssl.CERT_NONE}
)

print("Connected to Exasol successfully!")

# 2. Create Schema
C.execute("CREATE SCHEMA IF NOT EXISTS NETRA;")
C.execute("OPEN SCHEMA NETRA;")

# 3. Create Tables
C.execute("""
CREATE OR REPLACE TABLE cell_towers (
    tower_id VARCHAR(10) PRIMARY KEY,
    tower_name VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    coverage_radius_km DECIMAL(4,2),
    elevation_meters DECIMAL(5,2),
    battery_backup_hours INT,
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

print("Tables created successfully.")
# 25 Realistic Towers across Bengaluru with flood elevations
towers_data = [
    ('T01', 'Indiranagar 100ft Rd', 12.9784, 77.6408, 2.5, 3.2, 8, 'FAILED'),
    ('T02', 'Old Airport Road Junction', 12.9600, 77.6480, 3.0, 0.8, 4, 'FAILED'),
    ('T03', 'Domlur Flyover North', 12.9609, 77.6387, 2.0, 1.5, 6, 'ACTIVE'),
    ('T04', 'Koramangala 4th Block', 12.9352, 77.6245, 3.0, 0.5, 3, 'FAILED'),
    ('T05', 'MG Road Metro Station', 12.9756, 77.6066, 2.0, 4.0, 12, 'ACTIVE'),
    ('T06', 'Whitefield ITPL Main', 12.9860, 77.7300, 3.5, 2.8, 10, 'ACTIVE'),
    ('T07', 'Bellandur EcoSpace Ring Rd', 12.9260, 77.6762, 3.0, 0.4, 2, 'FAILED'),
    ('T08', 'Electronic City Phase 1', 12.8399, 77.6770, 3.5, 3.5, 10, 'ACTIVE'),
    ('T09', 'Silk Board Interchange', 12.9176, 77.6238, 2.5, 0.6, 4, 'FAILED'),
    ('T10', 'HSR Layout Sector 2', 12.9121, 77.6446, 2.8, 1.2, 6, 'ACTIVE'),
    ('T11', 'Marathahalli Bridge', 12.9591, 77.6974, 3.0, 1.0, 5, 'FAILED'),
    ('T12', 'Hebbal Flyover Hub', 13.0358, 77.5970, 3.5, 2.1, 8, 'ACTIVE'),
    ('T13', 'Shivajinagar Bus Station', 12.9856, 77.6057, 2.0, 2.9, 7, 'ACTIVE'),
    ('T14', 'Jayanagar 4th Block', 12.9299, 77.5824, 2.5, 3.8, 9, 'ACTIVE'),
    ('T15', 'BTM Layout 2nd Stage', 12.9166, 77.6101, 2.5, 1.1, 4, 'FAILED'),
    ('T16', 'Ulsoor Lake South', 12.9810, 77.6189, 2.0, 1.4, 6, 'ACTIVE'),
    ('T17', 'CV Raman Nagar DRDO', 12.9850, 77.6630, 2.8, 3.0, 10, 'ACTIVE'),
    ('T18', 'Sarjapur Wipro Gate', 12.9100, 77.6850, 3.0, 1.8, 6, 'ACTIVE'),
    ('T19', 'Yelahanka Airforce Hub', 13.1007, 77.5963, 4.0, 4.2, 12, 'ACTIVE'),
    ('T20', 'Rajajinagar Metro', 12.9982, 77.5530, 2.5, 3.6, 8, 'ACTIVE'),
    ('T21', 'Malleswaram 8th Cross', 13.0031, 77.5702, 2.0, 3.9, 9, 'ACTIVE'),
    ('T22', 'Banashankari Temple', 12.9255, 77.5468, 2.5, 3.7, 8, 'ACTIVE'),
    ('T23', 'Peenya Industrial Area', 13.0329, 77.5274, 3.5, 2.5, 7, 'ACTIVE'),
    ('T24', 'Majestic Railway Station', 12.9767, 77.5713, 2.0, 3.1, 10, 'ACTIVE'),
    ('T25', 'KR Puram Hanging Bridge', 13.0000, 77.6900, 3.0, 0.9, 3, 'FAILED')
]
C.import_from_iterable(towers_data, 'cell_towers')

# 12 Critical Lifeline Facilities
facilities_data = [
    ('F01', 'Manipal Hospital (ICU/Trauma)', 'HOSPITAL', 12.9592, 77.6475, 50),
    ('F02', 'Domlur Emergency Flood Shelter', 'SHELTER', 12.9615, 77.6350, 30),
    ('F03', 'Koramangala Fire & Rescue Station', 'FIRE_STATION', 12.9340, 77.6200, 40),
    ('F04', 'Bowring & Lady Curzon Hospital', 'HOSPITAL', 12.9830, 77.6030, 50),
    ('F05', 'Sakra World Hospital (Bellandur)', 'HOSPITAL', 12.9279, 77.6830, 50),
    ('F06', 'St. Johns National Academy Hospital', 'HOSPITAL', 12.9310, 77.6190, 50),
    ('F07', 'Bellandur Cyclone Evacuation Center', 'SHELTER', 12.9300, 77.6700, 30),
    ('F08', 'HSR Disaster Relief Base', 'SHELTER', 12.9150, 77.6400, 30),
    ('F09', 'HAL Central Fire Headquarters', 'FIRE_STATION', 12.9550, 77.6650, 40),
    ('F10', 'Columbia Asia Hospital Hebbal', 'HOSPITAL', 13.0380, 77.5920, 50),
    ('F11', 'Silk Board Emergency Medical Tent', 'SHELTER', 12.9180, 77.6250, 30),
    ('F12', 'Victoria General Hospital', 'HOSPITAL', 12.9630, 77.5750, 50)
]
C.import_from_iterable(facilities_data, 'critical_facilities')

# Connectivity & Redundancy Link Matrix
connectivity_data = [
    ('F01', 'T02', True),   # Manipal Hospital on T02 (Failed)
    ('F01', 'T03', False),  # Manipal Hospital backup on T03 (Active)
    ('F02', 'T03', True),   # Domlur Shelter on T03
    ('F03', 'T04', True),   # Fire Station on T04 (Failed - Zero Redundancy!)
    ('F04', 'T05', True),   # Bowring on T05
    ('F05', 'T07', True),   # Sakra on T07 (Failed)
    ('F05', 'T11', False),  # Sakra backup on T11 (Failed - Complete Blackout!)
    ('F06', 'T04', True),   # St Johns on T04 (Failed)
    ('F06', 'T15', False),  # St Johns backup on T15 (Failed - Complete Blackout!)
    ('F07', 'T07', True),   # Bellandur Shelter on T07 (Failed)
    ('F08', 'T10', True),   # HSR Shelter on T10
    ('F09', 'T02', True),   # HAL Fire on T02 (Failed)
    ('F10', 'T12', True),   # Columbia Asia on T12
    ('F11', 'T09', True),   # Silk Board Shelter on T09 (Failed)
    ('F12', 'T24', True)    # Victoria on T24
]
C.import_from_iterable(connectivity_data, 'facility_connectivity')

# 5 Special Response Repair Crews
crews_data = [
    ('C1', 'Alpha Rapid Response (GenSet)', 12.9716, 77.5946, 'GENERATOR_CREW', 'AVAILABLE'),
    ('C2', 'Bravo Amphibious Rescue Team', 12.9300, 77.6100, 'BOAT_UNIT', 'AVAILABLE'),
    ('C3', 'Charlie Fiber Splice Unit', 12.9800, 77.7200, 'FIBER_CREW', 'AVAILABLE'),
    ('C4', 'Delta Emergency Satellite Rig', 12.9100, 77.6500, 'SAT_LINK_CREW', 'AVAILABLE'),
    ('C5', 'Echo Heavy Power Logistics', 13.0300, 77.5800, 'GENERATOR_CREW', 'AVAILABLE')
]
C.import_from_iterable(crews_data, 'repair_crews')
print("All sample data successfully loaded into Exasol Personal!")
C.close()