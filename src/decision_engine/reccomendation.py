
from typing import Dict, List, Optional

from src.data_models.model import Tower, Crew, FacilityType
from src.decision_engine.cascade import simulate_cascade


def build_recommendation(
    top_tower: Tower,
    assigned_crew_id: str,
    impact_score: float,
    cascade_info: Dict,
    crews_by_id: Dict[str, Crew],
    towers_by_id: Dict[str, Tower],
    facilities_by_id: Dict,
    graph,
) -> Dict:
    """
    Return a formatted recommendation dict.

    Keys:
        - tower_id
        - priority_score (float)
        - assigned_crew_id
        - estimated_restoration_time (int minutes)
        - population_reconnected (int)
        - critical_facilities_reconnected (int)
        - justification (str)
    """
    # Get crew
    crew = crews_by_id.get(assigned_crew_id)
    restoration_time = top_tower.repair_time_estimate
    if crew:
        # Rough travel time estimate (could be refined)
        # For simplicity, we just use repair time; travel time will be added later if needed
        pass

    # Population reconnected = population covered by this tower
    population_reconnected = top_tower.population_covered

    # Critical facilities reconnected = count of critical facilities among those dependent
    # that were disconnected before restoration but now will be reconnected.
    # We can compute from cascade_info: number of critical facilities that this tower serves
    # and that were disconnected. But we have only overall count.
    # For a simple version, we assume all critical facilities served by this tower are reconnected.
    # Better: we can compute which facilities become reconnected when this tower is restored.
    # We'll compute the list of facilities this tower serves, and among them which are critical.
    dependent_fac_ids = get_dependent_facilities(graph, top_tower.id)  # need import
    critical_reconnected = 0
    for fid in dependent_fac_ids:
        fac = facilities_by_id.get(fid)
        if fac and fac.type in (FacilityType.HOSPITAL, FacilityType.SHELTER):
            # If the facility was disconnected (i.e., no active towers), restoring this tower will reconnect it
            # We can check current status from cascade_info? Actually cascade_info is before restoration.
            # We can recompute after restoring? To keep simple, we'll just count all critical facilities served.
            critical_reconnected += 1

    # Justification: compose from fragility and facility info
    # We'll build a generic template
    justifications = []
    if top_tower.redundancy_count == 0:
        justifications.append("has no redundant connectivity")
    else:
        justifications.append(f"has low redundancy ({top_tower.redundancy_count} alternatives)")

    # Check if it serves critical facilities
    critical_served = [f for f in dependent_fac_ids if facilities_by_id.get(f) and facilities_by_id[f].type in (FacilityType.HOSPITAL, FacilityType.SHELTER)]
    if critical_served:
        justifications.append(f"supports {len(critical_served)} critical facilities")

    justification = f"Tower {top_tower.id} " + ", ".join(justifications) + "."

    return {
        "tower_id": top_tower.id,
        "priority_score": round(impact_score, 2),
        "assigned_crew_id": assigned_crew_id,
        "estimated_restoration_time": restoration_time,
        "population_reconnected": population_reconnected,
        "critical_facilities_reconnected": critical_reconnected,
        "justification": justification,
    }


# Helper import (to avoid circular)
from src.decision_engine.dependency_graph import get_dependent_facilities