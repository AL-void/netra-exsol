import networkx as nx
import logging
from typing import List, Set, Dict
from src.data_models.model import Tower, Facility

logger = logging.getLogger(__name__)

def build_graph(towers: List[Tower], facilities: List[Facility]) -> nx.Graph:
    graph=nx.Graph()
    facility_ids={f.id for f in facilities}
    tower_ids={t.id for t in towers}
    for t in towers:
        graph.add_node(t.id,type="tower")
    for f in facilities:
        graph.add_node(f.id,type="facility")
    for t in towers:
        for fac_id in t.facilities_connected:
             if fac_id in facility_ids:
                  graph.add_edge(t.id,fac_id)
             else:
                logger.warning(f"Tower {t.id} references facility {fac_id} which does not exist in facility list.")
             
    for t in facilities:
            for tower_id in t.connected_towers:
                if tower_id not in tower_ids:
                    logger.warning(
                        f"Facility {t.id} references tower {tower_id} which does not exist in tower list. "
                        "Edge will be added anyway."
                    )
                # If the edge doesn't already exist, add it (union) and log a mismatch
                if not graph.has_edge(tower_id, f.id):
                    logger.warning(
                        f"Facility {f.id} lists tower {tower_id}, but that tower does not list this facility. "
                        "Adding edge to ensure connectivity from facility perspective."
                    )
                    graph.add_edge(tower_id, f.id)

    return graph

def get_dependent_facilities(graph, tower_id: str) -> List[str]:
    if tower_id not in graph:
        raise ValueError(f"Tower {tower_id} not found in graph")
    if graph.nodes[tower_id].get("type") != "tower":
        raise ValueError(f"Node {tower_id} is not a tower")

    neighbors = list(graph.neighbors(tower_id))
    # Filter only facility nodes (by type attribute)
    facilities = [n for n in neighbors if graph.nodes[n].get("type") == "facility"]
    return facilities

def get_serving_towers(graph, facility_id: str) -> List[str]:
    if facility_id not in graph:
        raise ValueError(f"Facility {facility_id} not found in graph")
    if graph.nodes[facility_id].get("type") != "facility":
        raise ValueError(f"Node {facility_id} is not a facility")

    neighbors = list(graph.neighbors(facility_id))
    towers = [n for n in neighbors if graph.nodes[n].get("type") == "tower"]
    return towers

def count_alternative_towers(graph: nx.Graph, tower_id: str) -> int:
    dependent_facilities = get_dependent_facilities(graph, tower_id)
    alternative_towers: Set[str] = set()
    for fac_id in dependent_facilities:
        serving = get_serving_towers(graph, fac_id)
        alternative_towers.update(serving)
    # Remove the tower itself
    alternative_towers.discard(tower_id)
    return len(alternative_towers)