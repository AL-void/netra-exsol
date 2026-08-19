import logging
from typing import List, Set, Dict
from src.data_models.model import Tower,Facility,Scenario,Tower_status
def apply_scenario_to_towers(scenario: Scenario, towers: List[Tower]) -> List[Tower]:
        updated = []
        for t in towers:
            # Copy to avoid mutating original (immutability)
            new_tower = t.model_copy()
            
            # Compute flood failure probability
            flood_threshold = 1.0 - (scenario.flood_level / 10.0)  # e.g., 1m -> 0.9, 5m -> 0.5
            if t.flood_risk > flood_threshold:
                new_tower.status = Tower_status.Failed
            else:
                # If flood isn't the cause, keep original status
                new_tower.status = t.status
            
            # Also reduce road accessibility
            new_tower.road_accessibility = t.road_accessibility * scenario.road_access_multiplier
            updated.append(new_tower)
        
        return updated