from dataclasses import dataclass
from pathlib import Path


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class SaveManifestDTO:
    display_name: str
    cold_location: Path
    hot_location: Path
