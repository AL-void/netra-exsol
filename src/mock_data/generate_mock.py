from src.data_models.model import Tower, Facility, Crew, Tower_status, FacilityType

def generate_mock_data():
    towers = [
        Tower(id="T1", location=(12.97, 77.59), population_covered=15000,
              facilities_connected=["F1", "F2"], redundancy_count=1,
              flood_risk=0.8, road_accessibility=0.6,
              status=Tower_status.Failed, repair_time_estimate=180),
        Tower(id="T2", location=(12.98, 77.60), population_covered=8000,
              facilities_connected=["F2"], redundancy_count=0,
              flood_risk=0.9, road_accessibility=0.4,
              status=Tower_status.Failed, repair_time_estimate=120),
        Tower(id="T5", location=(12.96, 77.58), population_covered=5000,
              facilities_connected=["F1"], redundancy_count=2,
              flood_risk=0.2, road_accessibility=1.0,
              status=Tower_status.Active, repair_time_estimate=60),
    ]
    facilities = [
        Facility(id="F1", type=FacilityType.HOSPITAL, connected_towers=["T1", "T5"]),
        Facility(id="F2", type=FacilityType.SHELTER, connected_towers=["T1", "T2"]),
    ]
    crews = [
        Crew(id="C1", location="T5", equipment_level=3, availability=True),
        Crew(id="C2", location="T2", equipment_level=2, availability=True),
    ]
    return towers, facilities, crews