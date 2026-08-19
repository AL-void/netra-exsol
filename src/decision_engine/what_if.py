from typing import List, Dict, Optional
import copy
import networkx as nx

from src.data_models.model import Tower, Facility, Crew, Scenario, Tower_status
from src.decision_engine.dependency_graph import build_graph
from src.decision_engine.fragility import fragility_score
from src.decision_engine.societal_impact_score import societal_impact_score
from src.decision_engine.cascade import simulate_cascade
from src.decision_engine.crew_optimization import assign_crews


def apply_scenario_to_towers(scenario: Scenario, towers: List[Tower]) -> List[Tower]:
    """
    Return a new list of towers with statuses updated based on scenario.

    Simplified flood failure logic:
    - tower fails if flood_risk > (1 - scenario.flood_level / 10)
    - road_accessibility is reduced by scenario.road_access_multiplier
    """
    updated = []
    for t in towers:
        # Copy to avoid mutation
        new_t = t.model_copy()
        # Flood failure threshold
        flood_threshold = 1.0 - (scenario.flood_level / 10.0)  # e.g. 1m -> 0.9, 5m -> 0.5
        if t.flood_risk > flood_threshold:
            new_t.status = Tower_status.Failed
        else:
            new_t.status = t.status
        # Reduce road accessibility
        new_t.road_accessibility = t.road_accessibility * scenario.road_access_multiplier
        updated.append(new_t)
    return updated


def run_scenario(
    scenario: Scenario,
    towers: List[Tower],
    facilities: List[Facility],
    crews: List[Crew],
    graph: Optional['nx.Graph'] = None,   # optional pre-built graph
) -> Dict:
    """
    Run the full decision pipeline for a single scenario.

    Returns a summary dict with:
        - scenario_id
        - failed_towers: list of tower IDs
        - impact_scores: dict {tower_id: score}
        - cascade: dict from simulate_cascade
        - assignment: dict {tower_id: crew_id}
        - top_recommendation: dict (to be filled by step 8)
    """
    # 1. Apply scenario to towers
    scenario_towers = apply_scenario_to_towers(scenario, towers)

    # 2. Build graph if not provided (edges don't change, but we can reuse)
    if graph is None:
        graph = build_graph(scenario_towers, facilities)

    # 3. Build lookup dicts
    towers_by_id = {t.id: t for t in scenario_towers}
    facilities_by_id = {f.id: f for f in facilities}

    # 4. Identify failed towers
    failed_towers = [t for t in scenario_towers if t.status == Tower_status.Failed]

    if not failed_towers:
        return {
            "scenario_id": scenario.id,
            "failed_towers": [],
            "impact_scores": {},
            "cascade": {"disconnected_facilities": [], "critical_facilities_lost": 0},
            "assignment": {},
            "top_recommendation": None,
        }

    # 5. Compute fragility and impact for each failed tower
    impact_scores = {}
    fragility_scores = {}
    for t in failed_towers:
        frag = fragility_score(graph, t, facilities_by_id, towers_by_id)
        fragility_scores[t.id] = frag
        impact = societal_impact_score(graph, t, facilities_by_id, towers_by_id, scenario)
        impact_scores[t.id] = impact

    # 6. Cascade analysis (current state)
    cascade_info = simulate_cascade(graph, towers_by_id, facilities_by_id)

    # 7. Crew assignment
    assignment = assign_crews(failed_towers, crews, impact_scores, towers_by_id)

    # 8. Build top recommendation (will be detailed in step 8)
    top_tower = None
    if assignment:
        # Find the tower with highest impact among those assigned
        assigned_tower_ids = list(assignment.keys())
        top_tower_id = max(assigned_tower_ids, key=lambda tid: impact_scores.get(tid, 0))
        top_tower = towers_by_id[top_tower_id]

    return {
        "scenario_id": scenario.id,
        "failed_towers": [t.id for t in failed_towers],
        "impact_scores": impact_scores,
        "fragility_scores": fragility_scores,
        "cascade": cascade_info,
        "assignment": assignment,
        "top_tower": top_tower,
    }


def compare_flood_levels(
    flood_levels: List[float],
    towers: List[Tower],
    facilities: List[Facility],
    crews: List[Crew],
    graph: Optional['nx.Graph'] = None,
) -> List[Dict]:
    """
    Run the pipeline for each flood level and return a list of summaries.
    """
    results = []
    for level in flood_levels:
        scenario = Scenario(
            id=f"flood_{level:.1f}m",
            flood_level=level,
            road_access_multiplier=1.0 - (level * 0.05),  # slight degradation
        )
        summary = run_scenario(scenario, towers, facilities, crews, graph)
        results.append(summary)
    return results