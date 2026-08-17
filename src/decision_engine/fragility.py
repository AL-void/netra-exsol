
import logging
from typing import Dict, List, Set
import networkx as nx
from src.config_loader import load_config
config = load_config()


from src.data_models.model import Tower, Facility, FacilityType,Tower_status
from src.decision_engine.dependency_graph import (
    get_dependent_facilities,
    get_serving_towers,
    count_alternative_towers,
)

logger = logging.getLogger(__name__)

WEIGHTS =config["fragility_weights"]
MAX_POPULATION_FOR_NORMALIZATION = 100_000  

def fragility_score(
    graph: nx.Graph,
    tower: Tower,
    facilities_by_id: Dict[str, Facility],
    towers_by_id: Dict[str, Tower],   # NEW
) -> float:
    """
    Compute fragility based on currently active towers only.
    """
    dep_fac_ids = get_dependent_facilities(graph, tower.id)
    total_deps = len(dep_fac_ids)

    if total_deps == 0:
        return 0.0

    # ---- 1. num_alternatives (only active towers) ----
    # Build set of active towers that serve at least one of our facilities
    active_alt_towers = set()
    for fac_id in dep_fac_ids:
        serving = get_serving_towers(graph, fac_id)
        for tw_id in serving:
            if tw_id == tower.id:
                continue
            tw_obj = towers_by_id.get(tw_id)
            if tw_obj and tw_obj.status == Tower_status.Active:
                active_alt_towers.add(tw_id)

    alt_count = len(active_alt_towers)
    alt_score = 1.0 / (1.0 + alt_count)

    # ---- 2. backup_unavailability (only active alternatives) ----
    facilities_with_alt = 0
    for fac_id in dep_fac_ids:
        serving = get_serving_towers(graph, fac_id)
        # Filter to active towers other than this one
        has_active_alt = any(
            tw_id != tower.id
            and towers_by_id.get(tw_id)
            and towers_by_id[tw_id].status == Tower_status.Active
            for tw_id in serving
        )
        if has_active_alt:
            facilities_with_alt += 1

    backup_availability = facilities_with_alt / total_deps
    backup_unavailability = 1.0 - backup_availability

    # ---- 3. critical_dependency ----
    critical_facilities_with_zero_alt = 0
    for fac_id in dep_fac_ids:
        fac = facilities_by_id.get(fac_id)
        if fac is None:
            continue
        if fac.type in (FacilityType.HOSPITAL, FacilityType.SHELTER):
            serving = get_serving_towers(graph, fac_id)
            has_active_alt = any(
                tw_id != tower.id
                and towers_by_id.get(tw_id)
                and towers_by_id[tw_id].status == Tower_status.Active
                for tw_id in serving
            )
            if not has_active_alt:
                critical_facilities_with_zero_alt += 1

    critical_score = critical_facilities_with_zero_alt / total_deps

    # ---- 4. population_no_alt ----
    if alt_count == 0:
        pop_score = min(tower.population_covered / MAX_POPULATION_FOR_NORMALIZATION, 1.0)
    else:
        pop_score = 0.0

    # ---- combine ----
    weighted_score = (
        WEIGHTS["num_alternatives"] * alt_score
        + WEIGHTS["backup_unavailability"] * backup_unavailability
        + WEIGHTS["critical_dependency"] * critical_score
        + WEIGHTS["population_no_alt"] * pop_score
    )
    return min(1.0, max(0.0, weighted_score))