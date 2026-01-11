"""
Rule-based decision making for agents.

This module provides smart decision-making logic for agents
based on their state and the world around them.
"""

from typing import Dict, Optional
from .agent import Agent
from .world import World
from .market import Market
from .config import MAX_HEALTH


class DecisionMaker:
    """Makes decisions for agents based on rules."""
    
    # Action IDs
    STAY = 0
    MOVE_NORTH = 1
    MOVE_SOUTH = 2
    MOVE_EAST = 3
    MOVE_WEST = 4
    BUY_FOOD = 5
    SELL_FOOD = 6
    BUY_ORE = 7
    SELL_ORE = 8
    BUY_TOOLS = 9
    SELL_TOOLS = 10
    PRODUCE = 11
    
    def __init__(self, world: World, market: Market):
        """Initialize decision maker with world and market context."""
        self.world = world
        self.market = market
    
    def decide_action(self, agent: Agent) -> int:
        """
        Decide what action an agent should take.
        
        Args:
            agent: The agent making the decision
        
        Returns:
            Action ID (0-11)
        """
        if agent.type == "consumer":
            return self._decide_consumer_action(agent)
        elif agent.type == "producer":
            return self._decide_producer_action(agent)
        elif agent.type == "trader":
            return self._decide_trader_action(agent)
        else:
            return self.STAY
    
    def _decide_consumer_action(self, agent: Agent) -> int:
        """
        Decision logic for consumers.
        
        Priority:
        1. Buy food if health is low or no food
        2. Move toward market if need food
        3. Sell excess food if have too much
        4. Random movement
        """
        # Priority 1: Buy food if health is low or no food
        food_inventory = agent.inventory.get("food", 0.0)
        food_price = self.market.get_price("food")
        
        # Urgent: Health is low or no food
        if agent.health < 50 or food_inventory < 2:
            # Try to buy food if can afford
            if agent.can_afford(food_price) and self.market.get_quantity("food") > 0:
                return self.BUY_FOOD
            
            # Move toward nearest market
            market = self.world.get_nearest_market(agent.x, agent.y)
            if market:
                return self._move_toward(agent, market.x, market.y)
        
        # Priority 2: Sell excess food if have too much
        if food_inventory > 5 and agent.wealth < 50:
            return self.SELL_FOOD
        
        # Priority 3: Random movement (explore)
        import random
        return random.choice([self.MOVE_NORTH, self.MOVE_SOUTH, self.MOVE_EAST, self.MOVE_WEST])
    
    def _decide_producer_action(self, agent: Agent) -> int:
        """
        Decision logic for producers.
        
        Priority:
        1. Produce if near resources
        2. Sell goods if have excess
        3. Buy ore if need it for production
        4. Move toward resources if not near any
        """
        cell = self.world.get_cell(agent.x, agent.y)
        adjacent_resources = self.world.get_adjacent_resource_cells(agent.x, agent.y)
        
        # Priority 1: Produce if near resources
        if adjacent_resources:
            # Check if near farm (can produce food)
            for resource in adjacent_resources:
                if resource.terrain_type == "farm":
                    # Produce food
                    return self.PRODUCE
            
            # Check if near mine (can produce tools if have ore)
            for resource in adjacent_resources:
                if resource.terrain_type == "mine":
                    if agent.has_inventory("ore", 2.0):
                        return self.PRODUCE
            
            # Near mine but no ore - try to buy ore
            ore_price = self.market.get_price("ore")
            if agent.can_afford(ore_price) and self.market.get_quantity("ore") > 0:
                return self.BUY_ORE
        
        # Priority 2: Sell goods if have excess
        food_inventory = agent.inventory.get("food", 0.0)
        tools_inventory = agent.inventory.get("tools", 0.0)
        
        if food_inventory > 3:
            return self.SELL_FOOD
        if tools_inventory > 2:
            return self.SELL_TOOLS
        
        # Priority 3: Move toward resources if not near any
        if not adjacent_resources:
            # Find nearest resource
            nearest_resource = self._find_nearest_resource(agent)
            if nearest_resource:
                return self._move_toward(agent, nearest_resource.x, nearest_resource.y)
        
        # Default: Stay or random movement
        import random
        return random.choice([self.STAY, self.MOVE_NORTH, self.MOVE_SOUTH, self.MOVE_EAST, self.MOVE_WEST])
    
    def _decide_trader_action(self, agent: Agent) -> int:
        """
        Decision logic for traders (arbitrage).
        
        Priority:
        1. Sell goods if price is high
        2. Buy goods if price is low
        3. Move toward market
        4. Random movement
        """
        # Get current prices
        food_price = self.market.get_price("food")
        ore_price = self.market.get_price("ore")
        tools_price = self.market.get_price("tools")
        
        # Priority 1: Sell goods if have them and price is good
        if agent.has_inventory("food", 1.0) and food_price > 1.2:
            return self.SELL_FOOD
        if agent.has_inventory("ore", 1.0) and ore_price > 1.5:
            return self.SELL_ORE
        if agent.has_inventory("tools", 1.0) and tools_price > 2.0:
            return self.SELL_TOOLS
        
        # Priority 2: Buy goods if price is low
        if food_price < 0.8 and agent.can_afford(food_price) and self.market.get_quantity("food") > 0:
            return self.BUY_FOOD
        if ore_price < 1.0 and agent.can_afford(ore_price) and self.market.get_quantity("ore") > 0:
            return self.BUY_ORE
        if tools_price < 1.5 and agent.can_afford(tools_price) and self.market.get_quantity("tools") > 0:
            return self.BUY_TOOLS
        
        # Priority 3: Move toward market
        market = self.world.get_nearest_market(agent.x, agent.y)
        if market:
            # Only move if not already at market
            if abs(agent.x - market.x) > 1 or abs(agent.y - market.y) > 1:
                return self._move_toward(agent, market.x, market.y)
        
        # Default: Random movement
        import random
        return random.choice([self.MOVE_NORTH, self.MOVE_SOUTH, self.MOVE_EAST, self.MOVE_WEST])
    
    def _move_toward(self, agent: Agent, target_x: int, target_y: int) -> int:
        """Decide which direction to move toward a target."""
        dx = target_x - agent.x
        dy = target_y - agent.y
        
        # Prefer moving in direction with larger difference
        if abs(dx) > abs(dy):
            if dx > 0:
                return self.MOVE_EAST
            elif dx < 0:
                return self.MOVE_WEST
        else:
            if dy > 0:
                return self.MOVE_NORTH
            elif dy < 0:
                return self.MOVE_SOUTH
        
        # If already at target, stay
        return self.STAY
    
    def _find_nearest_resource(self, agent: Agent):
        """Find the nearest resource cell (farm or mine) to the agent."""
        min_dist = float('inf')
        nearest = None
        
        for x in range(self.world.width):
            for y in range(self.world.height):
                cell = self.world.get_cell(x, y)
                if cell and cell.is_resource():
                    dist = abs(x - agent.x) + abs(y - agent.y)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = cell
        
        return nearest

