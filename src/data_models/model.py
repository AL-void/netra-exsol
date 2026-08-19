from __future__ import annotations
from pydantic import BaseModel, Field,field_validator,model_validator
from typing import List,Optional,Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Tower_status(str,Enum):
    Active="active"
    Failed="failed"
    Maintenance="maintenance"
    def is_operational(self)->bool:
        return self==Tower_status.Active
class FacilityType(str, Enum):
    HOSPITAL = "hospital"
    SHELTER = "shelter"
    EMERGENCY_CORRIDOR = "emergency_corridor"
    @property
    def critical_weight(self)->int:
        mapping={
            FacilityType.HOSPITAL:10,
            FacilityType.SHELTER:5,
            FacilityType.EMERGENCY_CORRIDOR:7
        }
        return mapping[self]

class Tower(BaseModel):

    id: str = Field(..., description="Unique tower identifier, e.g., 'T184'")
    
    # Geographic / Locational
    location: Optional[Tuple[float, float]] = Field( None, description="Latitude/Longitude for distance calculations")
    
    # Coverage & Dependency
    population_covered: int = Field(..., ge=0, description="Number of people served by this tower")
    facilities_connected: List[str] = Field(default_factory=list, description="List of Facility IDs dependent on this tower")
    redundancy_count: int = Field(default=0, ge=0, description="Number of alternative towers in the area")
    
    # Risk & Accessibility (Defaults assume no risk)
    flood_risk: float = Field( default=0.0, ge=0.0, le=1.0, description="Probability/severity of flooding (0-1)")
    road_accessibility: float = Field(default=1.0, ge=0.0, le=1.0, description="Accessibility for repair crews (1=fully accessible)")
    
    # Operational
    status: Tower_status = Field(..., description="Current operational status")
    repair_time_estimate: int = Field(..., gt=0, description="Estimated repair time in minutes")

    @model_validator(mode="after")
    def check_flood_contradiction(self) -> "Tower":
        """If flood risk is high but status is active, log a warning."""
        if self.flood_risk > 0.7 and self.status == Tower_status.Active:
            logger.warning(
                f"Tower {self.id} has high flood risk ({self.flood_risk}) "
                f"but is marked as ACTIVE. This may be inconsistent."
            )
        return self

    @field_validator("road_accessibility")
    @classmethod
    def validate_access(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("road_accessibility must be between 0 and 1")
        return v

class Facility(BaseModel):
    id: str = Field(..., description="Unique facility identifier, e.g., 'H2'")
    type: FacilityType = Field(..., description="Type of critical facility")
    
    # Relationship: IDs only (resolved by engine)
    connected_towers: List[str] = Field(default_factory=list, description="Tower IDs that provide connectivity to this facility")
    
    # Override weight if needed, but defaults to enum mapping
    custom_criticality_weight: Optional[int] = Field(default=None, ge=1, description="Optional override for criticality scoring")

    def get_effective_weight(self) -> int:
        return self.custom_criticality_weight or self.type.critical_weight

class Crew(BaseModel):
    id: str = Field(..., description="Crew identifier, e.g., 'C02'")
    location: str = Field(..., description="Tower ID where the crew is currently located")
    
    equipment_level: int = Field(default=1, ge=1, le=5, description="Capability level (1=basic, 5=advanced)")
    availability: bool = Field(default=True, description="Is the crew currently available for dispatch?")
    
    # Optional: For future advanced optimization
    travel_speed_factor: float = Field(default=1.0, ge=0.5, le=2.0, description="Multiplier for travel speed (1=nominal)")
    
    # Optional: Track current assignment to avoid overloading
    current_task: Optional[str] = Field(default=None, description="Tower ID currently being repaired, if any")

class Scenario(BaseModel):
    id: str = Field(..., description="Scenario identifier, e.g., 'flood_1m'")
    flood_level: float = Field(..., ge=0.0, description="Water level in meters")
    
    # Optional modifiers
    road_access_multiplier: float = Field(default=1.0, ge=0.0, le=1.0, description="Factor to reduce all tower road_accessibility (e.g., 0.8 for debris)")
    active_towers: List[str] = Field(default_factory=list)  # explicit override
    failed_towers: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(default=None, description="Human-readable scenario description")

    # --- Validators ---
    @field_validator("flood_level")
    @classmethod
    def flood_check(cls, v: float) -> float:
        if v > 5.0:
            logger.warning(f"Extreme flood level ({v}m) detected. Check input data.")
        return v
    def apply_scenario_to_towers(scenario: Scenario, towers: List[Tower]) -> List[Tower]:
        updated = []
        for t in towers:
            # Copy to avoid mutating original (immutability)
            new_tower = t.model_copy()
            
            # Compute flood failure probability
            flood_threshold = 1.0 - (scenario.flood_level / 10.0)  # e.g., 1m -> 0.9, 5m -> 0.5
            if t.flood_risk > flood_threshold:
                new_tower.status = Tower_status.Failed
            else:
                # If flood isn't the cause, keep original status
                new_tower.status = t.status
            
            # Also reduce road accessibility
            new_tower.road_accessibility = t.road_accessibility * scenario.road_access_multiplier
            updated.append(new_tower)
        
        return updated