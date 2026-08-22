from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Tower_status(str, Enum):
    Active = "active"
    Failed = "failed"
    Maintenance = "maintenance"

    def is_operational(self) -> bool:
        return self == Tower_status.Active

class FacilityType(str, Enum):
    HOSPITAL = "hospital"
    SHELTER = "shelter"
    EMERGENCY_CORRIDOR = "emergency_corridor"

    @property
    def critical_weight(self) -> int:
        mapping = {
            FacilityType.HOSPITAL: 10,
            FacilityType.SHELTER: 5,
            FacilityType.EMERGENCY_CORRIDOR: 7
        }
        return mapping[self]

class Tower(BaseModel):
    id: str = Field(..., description="Unique tower identifier")
    location: Optional[Tuple[float, float]] = Field(None, description="Latitude/Longitude")
    population_covered: int = Field(default=5000, ge=0)
    facilities_connected: List[str] = Field(default_factory=list)
    redundancy_count: int = Field(default=0, ge=0)
    flood_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    road_accessibility: float = Field(default=1.0, ge=0.0, le=1.0)
    status: Tower_status = Field(default=Tower_status.Active)
    repair_time_estimate: int = Field(default=45, gt=0)

    @field_validator("road_accessibility")
    @classmethod
    def validate_access(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("road_accessibility must be between 0 and 1")
        return v

class Facility(BaseModel):
    id: str = Field(...)
    name: Optional[str] = None
    type: FacilityType = Field(default=FacilityType.HOSPITAL)
    connected_towers: List[str] = Field(default_factory=list)
    custom_criticality_weight: Optional[int] = Field(default=None, ge=1)

    def get_effective_weight(self) -> int:
        return self.custom_criticality_weight or self.type.critical_weight

class Crew(BaseModel):
    id: str = Field(...)
    name: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    equipment_level: int = Field(default=1, ge=1, le=5)
    availability: bool = Field(default=True)
    travel_speed_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    current_task: Optional[str] = None

class Scenario(BaseModel):
    id: str = Field(...)
    flood_level: float = Field(..., ge=0.0)
    road_access_multiplier: float = Field(default=1.0, ge=0.0, le=1.0)
    active_towers: List[str] = Field(default_factory=list)
    failed_towers: List[str] = Field(default_factory=list)
    description: Optional[str] = None

def apply_scenario_to_towers(scenario: Scenario, towers: List[Tower]) -> List[Tower]:
    updated = []
    for t in towers:
        new_tower = t.model_copy()
        flood_threshold = 1.0 - (scenario.flood_level / 10.0)
        if t.flood_risk > flood_threshold:
            new_tower.status = Tower_status.Failed
        else:
            new_tower.status = t.status
        new_tower.road_accessibility = t.road_accessibility * scenario.road_access_multiplier
        updated.append(new_tower)
    return updated