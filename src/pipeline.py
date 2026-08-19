from src.mock_data.generate_mock import generate_mock_data
from src.decision_engine.dependency_graph import build_graph
from src.decision_engine.what_if import run_scenario
from src.decision_engine.reccomendation import build_recommendation
from src.decision_engine.alternative import compare_alternative
from src.data_models.model import Scenario

def run_decision(scenario: Scenario) -> dict:
    towers, facilities, crews = generate_mock_data()
    graph = build_graph(towers, facilities)

    summary = run_scenario(scenario, towers, facilities, crews, graph)

    if not summary["failed_towers"]:
        return {"message": "No failed towers in this scenario.", "scenario": summary}

    towers_by_id = {t.id: t for t in towers}
    facilities_by_id = {f.id: f for f in facilities}
    crews_by_id = {c.id: c for c in crews}
    failed_tower_objs = [towers_by_id[tid] for tid in summary["failed_towers"]]

    top_tower = summary["top_tower"]
    assigned_crew_id = summary["assignment"].get(top_tower.id)

    recommendation = build_recommendation(
        top_tower=top_tower,
        assigned_crew_id=assigned_crew_id,
        impact_score=summary["impact_scores"][top_tower.id],
        cascade_info=summary["cascade"],
        crews_by_id=crews_by_id,
        towers_by_id=towers_by_id,
        facilities_by_id=facilities_by_id,
        graph=graph,
    )

    alternative = compare_alternative(
        primary_recommendation=recommendation,
        failed_towers=failed_tower_objs,
        crews=crews,
        impact_scores=summary["impact_scores"],
        graph=graph,
        towers_by_id=towers_by_id,
        facilities_by_id=facilities_by_id,
    )

    return {
        "recommendation": recommendation,
        "alternative": alternative,
        "raw_summary": summary,
        "network": {
            "towers": [t.model_dump() for t in towers],
            "facilities": [f.model_dump() for f in facilities],
            "crews": [c.model_dump() for c in crews],
        },
    }


if __name__ == "__main__":
    scenario = Scenario(id="test_flood", flood_level=2.0, road_access_multiplier=0.9)
    result = run_decision(scenario)
    import json
    print(json.dumps(result, indent=2, default=str))