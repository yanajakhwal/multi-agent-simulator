"""
World and Cell classes for the simulation.

The World represents a 2D grid of cells, each with terrain types
(farm, mine, market, plain).
"""

import random
from typing import List, Literal, Optional
from dataclasses import dataclass

from .config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    FARM_PERCENTAGE,
    MINE_PERCENTAGE,
)


@dataclass
class Cell:
    """Represents a single cell in the world grid."""
    
    x: int
    y: int
    terrain_type: Literal["plain", "farm", "mine", "market"]
    base_yield: float = 0.0
    
    def __post_init__(self):
        """Set base_yield based on terrain type."""
        if self.terrain_type == "farm":
            self.base_yield = 1.0  # Can produce food
        elif self.terrain_type == "mine":
            self.base_yield = 1.0  # Can produce ore
        elif self.terrain_type == "market":
            self.base_yield = 0.0  # Markets don't produce, they trade
        else:  # plain
            self.base_yield = 0.0
    
    def is_resource(self) -> bool:
        """Check if this cell is a resource cell (farm or mine)."""
        return self.terrain_type in ["farm", "mine"]
    
    def is_market(self) -> bool:
        """Check if this cell is a market."""
        return self.terrain_type == "market"


class World:
    """Represents the 2D world grid with terrain."""
    
    def __init__(
        self,
        width: int = WORLD_WIDTH,
        height: int = WORLD_HEIGHT,
        farm_percentage: float = FARM_PERCENTAGE,
        mine_percentage: float = MINE_PERCENTAGE,
        seed: Optional[int] = None
    ):
        """
        Initialize the world with terrain.
        
        Args:
            width: Width of the world grid
            height: Height of the world grid
            farm_percentage: Percentage of cells that are farms (0-1)
            mine_percentage: Percentage of cells that are mines (0-1)
            seed: Random seed for reproducibility
        """
        self.width = width
        self.height = height
        self.farm_percentage = farm_percentage
        self.mine_percentage = mine_percentage
        
        if seed is not None:
            random.seed(seed)
        
        # Initialize grid with all plains
        self.cells: List[List[Cell]] = [
            [Cell(x=x, y=y, terrain_type="plain") for y in range(height)]
            for x in range(width)
        ]
        
        # Generate terrain
        self._generate_terrain()
    
    def _generate_terrain(self):
        """Generate farms, mines, and markets across the world."""
        total_cells = self.width * self.height
        num_farms = int(total_cells * self.farm_percentage)
        num_mines = int(total_cells * self.mine_percentage)
        
        # Get all cell positions
        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        random.shuffle(all_positions)
        
        # Place farms
        for i in range(num_farms):
            x, y = all_positions[i]
            self.cells[x][y].terrain_type = "farm"
            self.cells[x][y].base_yield = 1.0
        
        # Place mines
        for i in range(num_farms, num_farms + num_mines):
            x, y = all_positions[i]
            self.cells[x][y].terrain_type = "mine"
            self.cells[x][y].base_yield = 1.0
        
        # Place markets (fixed locations: center of each quadrant)
        # For Phase 1, place 2 markets in strategic locations
        market_positions = [
            (self.width // 4, self.height // 4),
            (3 * self.width // 4, 3 * self.height // 4),
        ]
        
        for x, y in market_positions:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.cells[x][y].terrain_type = "market"
                self.cells[x][y].base_yield = 0.0
    
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """Get cell at coordinates, or None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y]
        return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within world bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_adjacent_cells(self, x: int, y: int) -> List[Cell]:
        """Get all adjacent cells (north, south, east, west)."""
        adjacent = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # N, S, E, W
        
        for dx, dy in directions:
            cell = self.get_cell(x + dx, y + dy)
            if cell is not None:
                adjacent.append(cell)
        
        return adjacent
    
    def get_adjacent_resource_cells(self, x: int, y: int) -> List[Cell]:
        """Get adjacent cells that are resources (farms or mines)."""
        return [cell for cell in self.get_adjacent_cells(x, y) if cell.is_resource()]
    
    def get_nearest_market(self, x: int, y: int) -> Optional[Cell]:
        """Find the nearest market cell to given coordinates."""
        markets = []
        for row in self.cells:
            for cell in row:
                if cell.is_market():
                    markets.append(cell)
        
        if not markets:
            return None
        
        # Find closest market by Manhattan distance
        min_dist = float('inf')
        nearest = None
        for market in markets:
            dist = abs(market.x - x) + abs(market.y - y)
            if dist < min_dist:
                min_dist = dist
                nearest = market
        
        return nearest
    
    def count_terrain_type(self, terrain_type: str) -> int:
        """Count how many cells of a given terrain type exist."""
        count = 0
        for row in self.cells:
            for cell in row:
                if cell.terrain_type == terrain_type:
                    count += 1
        return count
    
    def __repr__(self) -> str:
        """String representation of the world."""
        terrain_counts = {
            "plain": self.count_terrain_type("plain"),
            "farm": self.count_terrain_type("farm"),
            "mine": self.count_terrain_type("mine"),
            "market": self.count_terrain_type("market"),
        }
        return (
            f"World({self.width}x{self.height}, "
            f"farms={terrain_counts['farm']}, "
            f"mines={terrain_counts['mine']}, "
            f"markets={terrain_counts['market']})"
        )

