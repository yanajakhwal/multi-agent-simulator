import random
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Agent:
    id: str
    role: str # either "consumer" or "producer" 
    wealth: float
    health: 10.0 
    inventory: Dict[str, float]

    def isAlive(self) -> bool:
        return self.health > 0


@dataclass
class Market:
    pass

@dataclass
class World:
    pass

def main():
    pass