#!/usr/bin/env python3
"""Simple test script to verify World class works."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.world import World
from src.core.config import WORLD_WIDTH, WORLD_HEIGHT

def main():
    print("🌍 Testing World class...")
    
    # Create world
    world = World(seed=42)  # Fixed seed for reproducibility
    print(f"Created: {world}")
    
    # Test cell access
    cell = world.get_cell(5, 5)
    print(f"Cell at (5, 5): {cell.terrain_type}")
    
    # Test bounds checking
    assert world.is_valid_position(0, 0) == True
    assert world.is_valid_position(-1, 0) == False
    assert world.is_valid_position(WORLD_WIDTH, 0) == False
    
    # Test adjacent cells
    adjacent = world.get_adjacent_cells(5, 5)
    print(f"Adjacent cells to (5, 5): {len(adjacent)} cells")
    
    # Count terrain types
    print(f"\nTerrain distribution:")
    print(f"  Plains: {world.count_terrain_type('plain')}")
    print(f"  Farms: {world.count_terrain_type('farm')}")
    print(f"  Mines: {world.count_terrain_type('mine')}")
    print(f"  Markets: {world.count_terrain_type('market')}")
    
    # Test market finding
    market = world.get_nearest_market(10, 10)
    if market:
        print(f"\nNearest market to (10, 10): ({market.x}, {market.y})")
    
    # Test resource detection
    resource_cells = world.get_adjacent_resource_cells(5, 5)
    print(f"\nAdjacent resource cells to (5, 5): {len(resource_cells)}")
    
    print("\n✅ World class tests passed!")

if __name__ == "__main__":
    main()

