"""
Configuration constants for Phase 1.
"""

# World configuration
WORLD_WIDTH = 30
WORLD_HEIGHT = 30

# Agent configuration
NUM_CONSUMERS = 12
NUM_PRODUCERS = 6
NUM_TRADERS = 4

# Economic parameters
PRICE_ALPHA = 0.1  # Price adjustment sensitivity
INITIAL_WEALTH_MIN = 50
INITIAL_WEALTH_MAX = 100
INITIAL_INVENTORY_MAX = 5

# Health & consumption
MAX_HEALTH = 100
HEALTH_DECAY_RATE = 1  # Health lost per tick without food
FOOD_CONSUMPTION_RATE = 1  # Food consumed per tick to maintain health
HEALTH_RECOVERY_RATE = 1  # Health gained per tick with food

# Production
ORE_TO_TOOLS_RATIO = 2  # 2 Ore → 1 Tool

# Terrain distribution (percentages)
FARM_PERCENTAGE = 0.12  # 12% of cells are farms
MINE_PERCENTAGE = 0.08  # 8% of cells are mines
MARKETS_PER_REGION = 2  # Fixed number of market cells per region

# Goods
GOODS = ["food", "ore", "tools"]

