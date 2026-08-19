from typing import Dict, List, Set
import networkx as nx

from src.data_models.model import Tower, Facility, Tower_status, FacilityType
from src.decision_engine.dependency_graph import get_serving_towers


def simulate_cascade(
    graph: nx.Graph,
    towers_by_id: Dict[str, Tower],
    facilities_by_id: Dict[str, Facility],
) -> Dict[str, object]:
    disconnected = []
    critical_count = 0

    for fac_id, facility in facilities_by_id.items():
        serving_towers = get_serving_towers(graph, fac_id)
        # Check if any active tower still serves this facility
        has_active = any(
            towers_by_id.get(t) and towers_by_id[t].status == Tower_status.Active
            for t in serving_towers
        )
        if not has_active:
            disconnected.append(fac_id)
            if facility.type in (FacilityType.HOSPITAL, FacilityType.SHELTER):
                critical_count += 1

    return {
        "disconnected_facilities": disconnected,
        "critical_facilities_lost": critical_count,
    }


def cascade_delta(
    graph: nx.Graph,
    towers_by_id: Dict[str, Tower],
    facilities_by_id: Dict[str, Facility],
    failed_tower_id: str,
) -> Dict[str, object]:
    # Capture state before failure
    before = simulate_cascade(graph, towers_by_id, facilities_by_id)

    # Mark tower as failed (mutate the provided dict)
    if failed_tower_id in towers_by_id:
        towers_by_id[failed_tower_id].status = Tower_status.FAILED

    # Capture state after
    after = simulate_cascade(graph, towers_by_id, facilities_by_id)

    # Newly disconnected facilities
    before_set = set(before["disconnected_facilities"])
    after_set = set(after["disconnected_facilities"])
    new_disconnected = list(after_set - before_set)

    # Critical count among new ones
    new_critical = sum(
        1 for fid in new_disconnected
        if facilities_by_id.get(fid)
        and facilities_by_id[fid].type in (FacilityType.HOSPITAL, FacilityType.SHELTER)
    )

    return {
        "newly_disconnected_facilities": new_disconnected,
        "new_critical_facilities_lost": new_critical,
        "total_disconnected": after["disconnected_facilities"],
        "total_critical_lost": after["critical_facilities_lost"],
    }