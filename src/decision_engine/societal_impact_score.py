import logging
from typing import Dict, List, Optional
import networkx as nx
from src.config_loader import load_config
config = load_config()

from src.data_models.model import Tower, Facility, Scenario, FacilityType
from src.decision_engine.dependency_graph import get_dependent_facilities
from src.decision_engine.fragility import fragility_score

logger = logging.getLogger(__name__)

# Configuration (hardcoded for now)
SOCIAL_WEIGHTS = config["impact_weights"]

# Normalization constants
MAX_POPULATION = 100_000      # 100k people = max pop impact
MAX_FACILITY_WEIGHT_SUM = 50  # 5 facilities * weight 10 (hospital) = max critical
MAX_FLOOD_LEVEL = 5.0         # meters


def societal_impact_score(
    graph: nx.Graph,
    tower: Tower,
    facilities_by_id: Dict[str, Facility],
    towers_by_id: Dict[str, Tower],
    scenario: Optional[Scenario] = None,
) -> float:
 
    dependent_fac_ids = get_dependent_facilities(graph, tower.id)
    
    # --- 1. pop_impact ---
    pop_impact = min(tower.population_covered / MAX_POPULATION, 1.0)
    
    # --- 2. critical_facilities ---
    total_weight = 0.0
    for fac_id in dependent_fac_ids:
        fac = facilities_by_id.get(fac_id)
        if fac:
            total_weight += fac.get_effective_weight()
    critical_impact = min(total_weight / MAX_FACILITY_WEIGHT_SUM, 1.0)
    
    # --- 3. vulnerable_pop (approx via flood_risk) ---
    vulnerable_pop = min((tower.flood_risk * tower.population_covered) / MAX_POPULATION, 1.0)
    
    # --- 4. fragility (already 0-1) ---
    fragility = fragility_score(
        graph=graph,
        tower=tower,
        facilities_by_id=facilities_by_id,
        towers_by_id=towers_by_id,
    )
    
    # --- 5. emergency_severity (scenario-level) ---
    if scenario and scenario.flood_level > 0:
        emergency_severity = min(scenario.flood_level / MAX_FLOOD_LEVEL, 1.0)
    else:
        emergency_severity = 0.0
    
    # --- Combine ---
    raw_score = (
        SOCIAL_WEIGHTS["pop_impact"] * pop_impact
        + SOCIAL_WEIGHTS["critical_facilities"] * critical_impact
        + SOCIAL_WEIGHTS["vulnerable_pop"] * vulnerable_pop
        + SOCIAL_WEIGHTS["fragility"] * fragility
        + SOCIAL_WEIGHTS["emergency_severity"] * emergency_severity
    )
    
    # Normalize to 0-100
    impact_100 = raw_score * 100.0
    
    return min(100.0, max(0.0, impact_100))