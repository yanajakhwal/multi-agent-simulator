"""
Simulation class that ties together World, Agents, and Market.

This is the main simulation loop for Phase 1 (single-process).
"""

import random
from typing import List, Dict, Optional
from collections import defaultdict

from .world import World, Cell
from .agent import Agent, Consumer, Producer, Trader, create_agent
from .market import Market
from .decision_maker import DecisionMaker
from .config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    NUM_CONSUMERS,
    NUM_PRODUCERS,
    NUM_TRADERS,
    MAX_HEALTH,
    HEALTH_DECAY_RATE,
    FOOD_CONSUMPTION_RATE,
    HEALTH_RECOVERY_RATE,
    ORE_TO_TOOLS_RATIO,
    GOODS,
)


class Simulation:
    """Main simulation class for Phase 1."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize simulation with world, agents, and market."""
        if seed is not None:
            random.seed(seed)
        
        # Create world
        self.world = World(seed=seed)
        
        # Create market
        self.market = Market()
        
        # Create agents
        self.agents: Dict[str, Agent] = {}
        self._create_agents()
        
        # Track tick
        self.tick = 0
        
        # Track metrics
        self.metrics = {
            "total_wealth": [],
            "agent_count": [],
            "avg_prices": defaultdict(list),
        }
        
        # Decision maker for smart agent actions
        self.decision_maker = DecisionMaker(self.world, self.market)
    
    def _create_agents(self):
        """Create and place agents in the world."""
        agent_id = 0
        
        # Create consumers (random placement)
        for _ in range(NUM_CONSUMERS):
            x = random.randint(0, WORLD_WIDTH - 1)
            y = random.randint(0, WORLD_HEIGHT - 1)
            agent = create_agent("consumer", f"c_{agent_id}", x, y)
            self.agents[agent.id] = agent
            agent_id += 1
        
        # Create producers (near resource cells)
        for _ in range(NUM_PRODUCERS):
            # Find a resource cell
            attempts = 0
            while attempts < 100:
                x = random.randint(0, WORLD_WIDTH - 1)
                y = random.randint(0, WORLD_HEIGHT - 1)
                cell = self.world.get_cell(x, y)
                
                # Check if near a resource cell (within 2 cells)
                nearby_resources = self.world.get_adjacent_resource_cells(x, y)
                if nearby_resources or (cell and cell.is_resource()):
                    agent = create_agent("producer", f"p_{agent_id}", x, y)
                    self.agents[agent.id] = agent
                    agent_id += 1
                    break
                attempts += 1
        
        # Create traders (random placement, prefer near markets)
        for _ in range(NUM_TRADERS):
            x = random.randint(0, WORLD_WIDTH - 1)
            y = random.randint(0, WORLD_HEIGHT - 1)
            agent = create_agent("trader", f"t_{agent_id}", x, y)
            self.agents[agent.id] = agent
            agent_id += 1
    
    def step(self, actions: Optional[Dict[str, int]] = None, use_smart_decisions: bool = True):
        """
        Execute one simulation step.
        
        Args:
            actions: Optional dict of agent_id -> action_id
                    If None, agents take smart actions (or random if use_smart_decisions=False)
            use_smart_decisions: If True, use rule-based decision making (default: True)
        """
        self.tick += 1
        
        if actions is None:
            if use_smart_decisions:
                actions = self._get_smart_actions()
            else:
                actions = self._get_random_actions()
        
        # Execute actions
        rewards = {}
        for agent_id, action_id in actions.items():
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                reward = self._execute_action(agent, action_id)
                rewards[agent_id] = reward
        
        # Update health/consumption
        self._update_health()
        
        # Update production
        self._update_production()
        
        # Update market prices
        self.market.update_prices()
        
        # Remove dead agents
        self._remove_dead_agents()
        
        # Update metrics
        self._update_metrics()
    
    def _get_smart_actions(self) -> Dict[str, int]:
        """Get smart rule-based actions for all agents."""
        actions = {}
        for agent_id, agent in self.agents.items():
            actions[agent_id] = self.decision_maker.decide_action(agent)
        return actions
    
    def _get_random_actions(self) -> Dict[str, int]:
        """Get random actions for all agents (fallback/legacy)."""
        actions = {}
        for agent_id in self.agents.keys():
            # Simple random actions: 0=stay, 1-4=move, 5-10=trade
            actions[agent_id] = random.randint(0, 10)
        return actions
    
    def _execute_action(self, agent: Agent, action_id: int) -> float:
        """
        Execute an action for an agent.
        
        Returns reward for this action.
        """
        initial_wealth = agent.wealth
        
        # Action mapping:
        # 0: Stay
        # 1-4: Move (N, S, E, W)
        # 5: Buy food
        # 6: Sell food
        # 7: Buy ore
        # 8: Sell ore
        # 9: Buy tools
        # 10: Sell tools
        # 11: Produce
        
        if action_id == 0:
            # Stay
            pass
        elif action_id == 1:
            # Move North
            agent.move(0, 1, WORLD_WIDTH, WORLD_HEIGHT)
        elif action_id == 2:
            # Move South
            agent.move(0, -1, WORLD_WIDTH, WORLD_HEIGHT)
        elif action_id == 3:
            # Move East
            agent.move(1, 0, WORLD_WIDTH, WORLD_HEIGHT)
        elif action_id == 4:
            # Move West
            agent.move(-1, 0, WORLD_WIDTH, WORLD_HEIGHT)
        elif action_id == 5:
            # Buy food
            success, cost = self.market.buy("food", 1.0)
            if success and agent.spend(cost):
                agent.add_inventory("food", 1.0)
        elif action_id == 6:
            # Sell food
            if agent.remove_inventory("food", 1.0):
                success, revenue = self.market.sell("food", 1.0)
                if success:
                    agent.earn(revenue)
        elif action_id == 7:
            # Buy ore
            success, cost = self.market.buy("ore", 1.0)
            if success and agent.spend(cost):
                agent.add_inventory("ore", 1.0)
        elif action_id == 8:
            # Sell ore
            if agent.remove_inventory("ore", 1.0):
                success, revenue = self.market.sell("ore", 1.0)
                if success:
                    agent.earn(revenue)
        elif action_id == 9:
            # Buy tools
            success, cost = self.market.buy("tools", 1.0)
            if success and agent.spend(cost):
                agent.add_inventory("tools", 1.0)
        elif action_id == 10:
            # Sell tools
            if agent.remove_inventory("tools", 1.0):
                success, revenue = self.market.sell("tools", 1.0)
                if success:
                    agent.earn(revenue)
        elif action_id == 11:
            # Produce (only for producers)
            if agent.type == "producer":
                self._try_produce(agent)
        
        # Compute reward
        wealth_delta = agent.wealth - initial_wealth
        
        if agent.type == "consumer":
            # Consumers: reward based on health changes (simplified)
            return wealth_delta * 0.1  # Small reward for wealth, will add health later
        else:
            # Producers/Traders: reward = profit
            return wealth_delta
    
    def _try_produce(self, agent: Producer):
        """Try to produce goods (if producer is near resources)."""
        cell = self.world.get_cell(agent.x, agent.y)
        if not cell:
            return
        
        adjacent_resources = self.world.get_adjacent_resource_cells(agent.x, agent.y)
        
        # Check for farm (food production)
        for resource_cell in adjacent_resources:
            if resource_cell.terrain_type == "farm":
                # Produce food
                agent.add_inventory("food", 1.0)
                self.market.add_supply("food", 1.0)
                return
        
        # Check for mine (ore or tool production)
        for resource_cell in adjacent_resources:
            if resource_cell.terrain_type == "mine":
                # Priority: Produce tools if have ore (higher value)
                if agent.remove_inventory("ore", ORE_TO_TOOLS_RATIO):
                    agent.add_inventory("tools", 1.0)
                    self.market.add_supply("tools", 1.0)
                    return
                
                # Otherwise, produce ore (raw material from mine)
                agent.add_inventory("ore", 1.0)
                self.market.add_supply("ore", 1.0)
                return
    
    def _update_health(self):
        """Update agent health based on food consumption."""
        for agent in self.agents.values():
            if agent.type == "consumer":
                # Consumers need food
                if agent.remove_inventory("food", FOOD_CONSUMPTION_RATE):
                    # Consumed food, recover health
                    agent.health = min(MAX_HEALTH, agent.health + HEALTH_RECOVERY_RATE)
                else:
                    # No food, lose health
                    agent.health -= HEALTH_DECAY_RATE
            else:
                # Producers/Traders also need food (simplified)
                if agent.remove_inventory("food", FOOD_CONSUMPTION_RATE):
                    agent.health = min(MAX_HEALTH, agent.health + HEALTH_RECOVERY_RATE)
                else:
                    agent.health -= HEALTH_DECAY_RATE
    
    def _update_production(self):
        """Update production for producers (simplified - happens automatically)."""
        # Production happens via actions, so this is a placeholder
        pass
    
    def _remove_dead_agents(self):
        """Remove agents that have died."""
        dead_ids = [
            agent_id for agent_id, agent in self.agents.items()
            if not agent.is_alive()
        ]
        for agent_id in dead_ids:
            del self.agents[agent_id]
    
    def _update_metrics(self):
        """Update simulation metrics."""
        total_wealth = sum(agent.wealth for agent in self.agents.values())
        self.metrics["total_wealth"].append(total_wealth)
        self.metrics["agent_count"].append(len(self.agents))
        
        for good in GOODS:
            self.metrics["avg_prices"][good].append(self.market.get_price(good))
    
    def get_state_summary(self) -> Dict:
        """Get summary of current simulation state."""
        return {
            "tick": self.tick,
            "num_agents": len(self.agents),
            "total_wealth": sum(agent.wealth for agent in self.agents.values()),
            "prices": {
                good: self.market.get_price(good) for good in GOODS
            },
            "market_quantities": {
                good: self.market.get_quantity(good) for good in GOODS
            },
        }

