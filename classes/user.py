from dataclasses import dataclass
from typing import List


@dataclass
class User:
    id: str
    ratings: List[tuple[str, float]]
