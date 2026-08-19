import math
import logging
from typing import Dict, List, Tuple, Optional
from scipy.optimize import linear_sum_assignment

from src.data_models.model import Tower, Crew

logger = logging.getLogger(__name__)

# Constants for travel time estimation
DEFAULT_TRAVEL_TIME = 15.0      # minutes if no coordinates
AVERAGE_SPEED_KMPH = 30.0       # km/h for rough travel time
EARTH_RADIUS_KM = 6371.0        # for haversine (if we want to be precise)

# Optional: if we have lat/lon, we can compute distance; otherwise use default.
def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate great-circle distance in km."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * EARTH_RADIUS_KM * math.atan2(math.sqrt(a), math.sqrt(1-a))


# We'll redefine the actual function to accept towers_by_id.
def assign_crews(
    failed_towers: List[Tower],
    crews: List[Crew],
    impact_scores: Dict[str, float],
    towers_by_id: Dict[str, Tower],
) -> Dict[str, str]:
    # 1. Filter available crews
    available_crews = [c for c in crews if c.availability]
    if not available_crews:
        logger.warning("No available crews for dispatch.")
        return {}

    if not failed_towers:
        return {}

    # 2. Sort failed towers by impact (descending) and take top K
    K = len(available_crews)
    sorted_failed = sorted(failed_towers, key=lambda t: impact_scores.get(t.id, 0.0), reverse=True)
    selected_towers = sorted_failed[:K]

    if not selected_towers:
        return {}

    # 3. Build benefit matrix: rows = crews, cols = selected towers
    benefits = []
    for crew in available_crews:
        row = []
        crew_location = towers_by_id.get(crew.location)  # crew's tower
        crew_lat = crew_location.location[0] if crew_location and crew_location.location else None
        crew_lon = crew_location.location[1] if crew_location and crew_location.location else None

        for tower in selected_towers:
            # Travel time estimation
            if crew_lat is not None and tower.location is not None:
                dist = _haversine_distance(crew_lat, crew_lon, tower.location[0], tower.location[1])
                travel_time = (dist / AVERAGE_SPEED_KMPH) * 60.0  # km/h -> minutes
            else:
                travel_time = DEFAULT_TRAVEL_TIME

            repair_time = tower.repair_time_estimate
            total_time = travel_time + repair_time

            impact = impact_scores.get(tower.id, 0.0)
            # Benefit = impact / (travel + repair) ; if total_time=0, set benefit to large
            if total_time > 0:
                benefit = impact / total_time
            else:
                benefit = impact * 1000.0  # if zero time, high benefit

            row.append(benefit)
        benefits.append(row)

    # Convert to cost matrix: negative benefit (minimize cost)
    cost_matrix = [[-b for b in row] for row in benefits]

    # 4. Solve assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # 5. Build result mapping
    assignment = {}
    for r, c in zip(row_ind, col_ind):
        crew = available_crews[r]
        tower = selected_towers[c]
        assignment[tower.id] = crew.id

    return assignment