"""
Agent classes for the simulation.

Agents can be consumers, producers, or traders, each with different
behaviors and reward structures.
"""

import random
from typing import Dict, Literal, Optional
from dataclasses import dataclass, field

from .config import (
    MAX_HEALTH,
    INITIAL_WEALTH_MIN,
    INITIAL_WEALTH_MAX,
    INITIAL_INVENTORY_MAX,
    GOODS,
)


@dataclass
class Agent:
    """Base agent class."""
    
    id: str
    type: Literal["consumer", "producer", "trader"]
    x: int
    y: int
    wealth: float
    health: float
    inventory: Dict[str, float] = field(default_factory=dict)
    region_id: str = "default"  # Phase 1: single region
    
    def __post_init__(self):
        """Initialize inventory if empty."""
        if not self.inventory:
            self.inventory = {good: 0.0 for good in GOODS}
    
    def is_alive(self) -> bool:
        """Check if agent is alive."""
        return self.health > 0
    
    def can_afford(self, price: float) -> bool:
        """Check if agent can afford a price."""
        return self.wealth >= price
    
    def has_inventory(self, good: str, quantity: float = 1.0) -> bool:
        """Check if agent has enough of a good."""
        return self.inventory.get(good, 0.0) >= quantity
    
    def add_inventory(self, good: str, quantity: float):
        """Add goods to inventory."""
        if good not in self.inventory:
            self.inventory[good] = 0.0
        self.inventory[good] += quantity
    
    def remove_inventory(self, good: str, quantity: float) -> bool:
        """Remove goods from inventory. Returns True if successful."""
        if not self.has_inventory(good, quantity):
            return False
        self.inventory[good] -= quantity
        return True
    
    def spend(self, amount: float) -> bool:
        """Spend wealth. Returns True if successful."""
        if self.wealth < amount:
            return False
        self.wealth -= amount
        return True
    
    def earn(self, amount: float):
        """Earn wealth."""
        self.wealth += amount
    
    def move(self, dx: int, dy: int, world_width: int, world_height: int) -> bool:
        """Move agent. Returns True if move was valid."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 <= new_x < world_width and 0 <= new_y < world_height:
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def __repr__(self) -> str:
        return (
            f"Agent(id={self.id}, type={self.type}, "
            f"pos=({self.x}, {self.y}), wealth={self.wealth:.1f}, "
            f"health={self.health:.1f})"
        )


class Consumer(Agent):
    """Consumer agents need food to survive."""
    
    def __init__(
        self,
        agent_id: str,
        x: int,
        y: int,
        wealth: Optional[float] = None,
        health: float = MAX_HEALTH,
        inventory: Optional[Dict[str, float]] = None
    ):
        """Initialize a consumer agent."""
        if wealth is None:
            wealth = random.uniform(INITIAL_WEALTH_MIN, INITIAL_WEALTH_MAX)
        
        if inventory is None:
            inventory = {
                good: random.uniform(0, INITIAL_INVENTORY_MAX)
                for good in GOODS
            }
        
        super().__init__(
            id=agent_id,
            type="consumer",
            x=x,
            y=y,
            wealth=wealth,
            health=health,
            inventory=inventory
        )


class Producer(Agent):
    """Producer agents convert resources into goods."""
    
    def __init__(
        self,
        agent_id: str,
        x: int,
        y: int,
        wealth: Optional[float] = None,
        health: float = MAX_HEALTH,
        inventory: Optional[Dict[str, float]] = None
    ):
        """Initialize a producer agent."""
        if wealth is None:
            wealth = random.uniform(INITIAL_WEALTH_MIN, INITIAL_WEALTH_MAX)
        
        if inventory is None:
            inventory = {
                good: random.uniform(0, INITIAL_INVENTORY_MAX)
                for good in GOODS
            }
        
        super().__init__(
            id=agent_id,
            type="producer",
            x=x,
            y=y,
            wealth=wealth,
            health=health,
            inventory=inventory
        )
    
    def can_produce_food(self) -> bool:
        """Check if producer can produce food (needs to be near farm)."""
        # This will be checked by the simulation based on location
        return True
    
    def can_produce_tools(self) -> bool:
        """Check if producer can produce tools (needs ore and to be near mine)."""
        # This will be checked by the simulation based on location and inventory
        return self.has_inventory("ore", 2.0)


class Trader(Agent):
    """Trader agents buy and sell goods for profit."""
    
    def __init__(
        self,
        agent_id: str,
        x: int,
        y: int,
        wealth: Optional[float] = None,
        health: float = MAX_HEALTH,
        inventory: Optional[Dict[str, float]] = None
    ):
        """Initialize a trader agent."""
        if wealth is None:
            wealth = random.uniform(INITIAL_WEALTH_MIN, INITIAL_WEALTH_MAX)
        
        if inventory is None:
            inventory = {
                good: random.uniform(0, INITIAL_INVENTORY_MAX)
                for good in GOODS
            }
        
        super().__init__(
            id=agent_id,
            type="trader",
            x=x,
            y=y,
            wealth=wealth,
            health=health,
            inventory=inventory
        )


def create_agent(
    agent_type: Literal["consumer", "producer", "trader"],
    agent_id: str,
    x: int,
    y: int,
    **kwargs
) -> Agent:
    """Factory function to create agents."""
    if agent_type == "consumer":
        return Consumer(agent_id, x, y, **kwargs)
    elif agent_type == "producer":
        return Producer(agent_id, x, y, **kwargs)
    elif agent_type == "trader":
        return Trader(agent_id, x, y, **kwargs)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

