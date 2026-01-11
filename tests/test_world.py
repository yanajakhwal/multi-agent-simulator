"""
Pytest tests for World class.

Run with: pytest tests/test_world.py -v
"""

import pytest
from src.core.world import World, Cell
from src.core.config import WORLD_WIDTH, WORLD_HEIGHT


class TestWorld:
    """Test suite for World class."""
    
    def test_world_creation(self):
        """Test world is created with correct dimensions."""
        world = World(seed=42)
        assert world.width == WORLD_WIDTH
        assert world.height == WORLD_HEIGHT
        assert len(world.cells) == WORLD_WIDTH
        assert len(world.cells[0]) == WORLD_HEIGHT
    
    def test_cell_access(self):
        """Test accessing cells."""
        world = World(seed=42)
        
        # Valid position
        cell = world.get_cell(5, 5)
        assert cell is not None
        assert cell.x == 5
        assert cell.y == 5
        
        # Invalid position
        assert world.get_cell(-1, 0) is None
        assert world.get_cell(WORLD_WIDTH, 0) is None
    
    def test_is_valid_position(self):
        """Test position validation."""
        world = World(seed=42)
        
        # Valid positions
        assert world.is_valid_position(0, 0) == True
        assert world.is_valid_position(WORLD_WIDTH - 1, WORLD_HEIGHT - 1) == True
        
        # Invalid positions
        assert world.is_valid_position(-1, 0) == False
        assert world.is_valid_position(0, -1) == False
        assert world.is_valid_position(WORLD_WIDTH, 0) == False
        assert world.is_valid_position(0, WORLD_HEIGHT) == False
    
    def test_adjacent_cells(self):
        """Test getting adjacent cells."""
        world = World(seed=42)
        
        # Center cell should have 4 adjacent
        adjacent = world.get_adjacent_cells(5, 5)
        assert len(adjacent) == 4
        
        # Corner cell should have 2 adjacent
        adjacent = world.get_adjacent_cells(0, 0)
        assert len(adjacent) == 2
    
    def test_terrain_generation(self):
        """Test terrain is generated correctly."""
        world = World(seed=42)
        
        # Should have farms
        farms = world.count_terrain_type("farm")
        assert farms > 0
        
        # Should have mines
        mines = world.count_terrain_type("mine")
        assert mines > 0
        
        # Should have markets
        markets = world.count_terrain_type("market")
        assert markets > 0
        
        # Should have mostly plains
        plains = world.count_terrain_type("plain")
        assert plains > farms + mines
    
    def test_cell_is_resource(self):
        """Test resource cell detection."""
        world = World(seed=42)
        
        # Find a farm cell
        for row in world.cells:
            for cell in row:
                if cell.terrain_type == "farm":
                    assert cell.is_resource() == True
                    assert cell.is_market() == False
                    break
    
    def test_nearest_market(self):
        """Test finding nearest market."""
        world = World(seed=42)
        
        market = world.get_nearest_market(10, 10)
        assert market is not None
        assert market.is_market() == True


class TestCell:
    """Test suite for Cell class."""
    
    def test_cell_creation(self):
        """Test cell creation."""
        cell = Cell(x=5, y=10, terrain_type="farm")
        assert cell.x == 5
        assert cell.y == 10
        assert cell.terrain_type == "farm"
        assert cell.base_yield == 1.0
    
    def test_cell_base_yield(self):
        """Test base yield is set correctly."""
        farm = Cell(x=0, y=0, terrain_type="farm")
        assert farm.base_yield == 1.0
        
        mine = Cell(x=0, y=0, terrain_type="mine")
        assert mine.base_yield == 1.0
        
        plain = Cell(x=0, y=0, terrain_type="plain")
        assert plain.base_yield == 0.0
        
        market = Cell(x=0, y=0, terrain_type="market")
        assert market.base_yield == 0.0

