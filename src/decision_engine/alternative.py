from typing import Dict, List, Optional
import copy

from src.data_models.model import Tower, Crew, Tower_status, FacilityType
from src.decision_engine.crew_optimization import assign_crews
from src.decision_engine.cascade import simulate_cascade
from src.decision_engine.dependency_graph import get_dependent_facilities


def compute_state_metrics(
    restored_tower_ids: List[str],
    failed_towers: List[Tower],
    towers_by_id: Dict[str, Tower],
    facilities_by_id: Dict,
    graph,
) -> Dict:
    """
    Given a list of tower IDs that are restored (set to ACTIVE),
    return metrics about the resulting state.

    Returns:
        - affected_population: total population of still-failed towers
        - critical_facilities_lost: from cascade simulation
        - still_failed_towers: list of tower IDs still failed
    """
    # Make a copy of towers_by_id to mutate
    state = {tid: t.model_copy() for tid, t in towers_by_id.items()}

    # Mark restored towers as ACTIVE
    for tid in restored_tower_ids:
        if tid in state:
            state[tid].status = Tower_status.Active

    # Run cascade on this state
    cascade = simulate_cascade(graph, state, facilities_by_id)

    # Compute affected population: sum of population of still-failed towers
    still_failed = [t for t in failed_towers if t.id not in restored_tower_ids]
    affected_pop = sum(t.population_covered for t in still_failed)

    return {
        "affected_population": affected_pop,
        "critical_facilities_lost": cascade["critical_facilities_lost"],
        "still_failed_towers": [t.id for t in still_failed],
    }


def compare_alternative(
    primary_recommendation: Dict,
    failed_towers: List[Tower],
    crews: List[Crew],
    impact_scores: Dict[str, float],
    graph,
    towers_by_id: Dict[str, Tower],
    facilities_by_id: Dict,
) -> Dict:
    """
    Compare primary decision (restore top tower) vs alternative (restore second-best tower).

    Returns:
        {
            "primary": {metrics...},
            "alternative": {metrics...},
            "delta": {
                "population_difference": alt_pop - primary_pop,
                "critical_facilities_difference": alt_critical - primary_critical,
                "time_difference": alt_time - primary_time
            }
        }
    """
    # 1. Identify top and second-best towers
    top_tower_id = primary_recommendation.get("tower_id")
    if not top_tower_id:
        return {"error": "No top tower in primary recommendation."}

    # Find second-best tower by impact score
    sorted_failed = sorted(failed_towers, key=lambda t: impact_scores.get(t.id, 0.0), reverse=True)
    if len(sorted_failed) < 2:
        return {"error": "Not enough failed towers for alternative comparison."}

    top_tower = sorted_failed[0]
    second_tower = sorted_failed[1]

    # 2. Primary: restore top tower
    primary_restored = [top_tower_id]
    primary_metrics = compute_state_metrics(
        restored_tower_ids=primary_restored,
        failed_towers=failed_towers,
        towers_by_id=towers_by_id,
        facilities_by_id=facilities_by_id,
        graph=graph,
    )

    # 3. Alternative: restore second-best tower
    # But we need to know which crew would be assigned to it in the alternative scenario.
    # Re-run crew assignment on failed towers *excluding the top tower* (so the second tower gets a crew)
    remaining_failed = [t for t in failed_towers if t.id != top_tower_id]
    alt_assignment = assign_crews(remaining_failed, crews, impact_scores, towers_by_id)

    # If the second tower didn't get assigned (e.g., no crews left), we can't proceed
    if second_tower.id not in alt_assignment:
        return {"error": f"Second tower {second_tower.id} could not be assigned a crew in alternative."}

    alternative_restored = list(alt_assignment.keys())  # may include more than one tower
    # We only care about the second tower being restored, but we might have others as well.
    # However, the alternative scenario is: restore second tower *first*, then possibly others.
    # For fairness, we should only mark the second tower as restored (since that's the "decision").
    # Others might be restored later, but for comparison we want to isolate the decision.
    # So we'll create a state where ONLY the second tower is restored.
    alt_restored = [second_tower.id]
    alternative_metrics = compute_state_metrics(
        restored_tower_ids=alt_restored,
        failed_towers=failed_towers,
        towers_by_id=towers_by_id,
        facilities_by_id=facilities_by_id,
        graph=graph,
    )

    # 4. Time difference: use restoration times (repair + travel) for each tower's assigned crew
    primary_crew_id = primary_recommendation.get("assigned_crew_id")
    primary_time = primary_recommendation.get("estimated_restoration_time", 0)

    # Alternative time: find crew assigned to second tower
    alt_crew_id = alt_assignment.get(second_tower.id)
    alt_time = 0
    if alt_crew_id:
        # Find the crew object to get travel speed? We'll just use repair time for now
        alt_time = second_tower.repair_time_estimate  # could add travel time later

    # 5. Compute deltas: alternative - primary
    delta_pop = alternative_metrics["affected_population"] - primary_metrics["affected_population"]
    delta_critical = alternative_metrics["critical_facilities_lost"] - primary_metrics["critical_facilities_lost"]
    delta_time = alt_time - primary_time

    return {
        "primary": {
            "tower_restored": top_tower_id,
            "crew_used": primary_crew_id,
            "affected_population": primary_metrics["affected_population"],
            "critical_facilities_lost": primary_metrics["critical_facilities_lost"],
        },
        "alternative": {
            "tower_restored": second_tower.id,
            "crew_used": alt_crew_id,
            "affected_population": alternative_metrics["affected_population"],
            "critical_facilities_lost": alternative_metrics["critical_facilities_lost"],
        },
        "delta": {
            "population_difference": delta_pop,
            "critical_facilities_difference": delta_critical,
            "time_difference": delta_time,
        }
    }