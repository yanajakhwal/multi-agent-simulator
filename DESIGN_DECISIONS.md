# Design Decisions - Multi-Agent Economy Simulator

**Date:** January 2026  
**Status:** Finalized for Phase 1

---

## Decision 1: Action Space Design

### Options:
- **A) Fixed quantity per action** - Each "buy food" action buys exactly 1 unit
- **B) Parameterized actions** - Action + quantity parameter (e.g., buy 1-5 units)
- **C) Separate actions per quantity** - "Buy 1 food", "Buy 2 food", etc. (larger action space)

### Decision: **Option A - Fixed quantity per action**

### Rationale:
- Simplest to implement and debug
- Smaller action space (easier for RL later)
- Clear semantics: one action = one unit transaction
- Can always extend to parameterized later if needed

### Implementation:
- Each buy/sell action operates on exactly 1 unit
- If agent can't afford 1 unit, action fails (no-op or small penalty)
- Action space size: ~9 actions (stay, 4 directions, buy food, sell food, buy ore, sell ore, produce)

---

## Decision 2: Tick Duration

### Options:
- **A) Real-time with fixed tick rate** - Sleep between ticks (e.g., 1 tick/second)
- **B) As-fast-as-possible** - No sleep, run simulation as quickly as possible
- **C) Configurable** - Command-line flag to set tick rate

### Decision: **Option B - As-fast-as-possible (with optional configurable sleep)**

### Rationale:
- Faster iteration and testing
- Can add sleep later if needed for visualization
- More flexible: can run 1000 ticks quickly for testing, slow down for demo
- Real-time not needed until dashboard/visualization phase

### Implementation:
- Default: no sleep (as-fast-as-possible)
- Optional: `--tick-rate` CLI argument (e.g., `--tick-rate 0.1` = 10 ticks/sec)
- For Phase 1: pure speed, no sleep

---

## Decision 3: Agent Initialization

### Options:
- **A) Random placement** - All agents placed randomly across world
- **B) Structured placement** - Producers near resources, traders near borders, consumers spread out
- **C) Hybrid** - Random but with constraints (e.g., producers must be near farm/mine cells)

### Decision: **Option C - Hybrid (Random with constraints)**

### Rationale:
- More realistic starting state (producers near resources)
- Still has randomness for variety
- Better for testing economic dynamics (producers can actually produce)
- Avoids degenerate states (e.g., producer stuck in middle of nowhere)

### Implementation:
- **Consumers**: Random placement anywhere
- **Producers**: Random placement within 2 cells of a resource cell (farm or mine)
- **Traders**: Random placement, but prefer near region borders (if multi-region) or market cells
- All agents start with:
  - Wealth: Random uniform [50, 100]
  - Health: 100 (max)
  - Inventory: Random small amounts [0, 5] of each good

---

## Decision 4: World Size

### Options:
- **A) Small (20×20)** - 400 cells, easier to debug
- **B) Design size (50×50)** - 2500 cells, matches final vision
- **C) Configurable** - Parameter that can be changed

### Decision: **Option C - Configurable (default: 30×30 for Phase 1)**

### Rationale:
- Start medium-sized (30×30 = 900 cells) - not too small, not overwhelming
- Easy to scale up/down for testing
- 30×30 is good for:
  - Testing sharding logic (can split into 2-3 regions easily)
  - Visualizing in terminal/UI
  - Fast enough for iteration
- Can increase to 50×50 for Phase 2+

### Implementation:
- Default: `WORLD_WIDTH = 30`, `WORLD_HEIGHT = 30`
- Configurable via config file or CLI: `--world-size 50 50`
- For Phase 1: stick with 30×30

---

## Decision 5: Number of Goods

### Options:
- **A) Minimal (2 goods)** - Food + one resource (e.g., ore)
- **B) Standard (3 goods)** - Food + Ore + Tools (production chain)
- **C) Rich (4+ goods)** - Multiple resources, multiple products

### Decision: **Option B - Standard (3 goods: Food, Ore, Tools)**

### Rationale:
- Creates interesting production chain: Ore → Tools → (used by producers)
- Not too simple (2 goods), not too complex (4+ goods)
- Good for testing:
  - Consumers need Food
  - Producers convert Ore → Tools
  - Traders can arbitrage all three
- Can add more goods later easily

### Implementation:
- **Food**: Consumed by all agents (health maintenance)
- **Ore**: Raw resource, mined from mine cells
- **Tools**: Produced from Ore, used for production efficiency (optional bonus)
- Market tracks all three goods
- Agents can hold inventory of all three

---

## Additional Decisions

### Decision 6: Number of Agents (Phase 1)

**Decision:** Start with 20-30 agents total

**Breakdown:**
- 10-15 Consumers
- 5-8 Producers  
- 3-5 Traders

**Rationale:**
- Enough for interesting dynamics
- Not too many to debug
- Can scale up later

---

### Decision 7: Terrain Distribution

**Decision:** Structured terrain layout

**Implementation:**
- **Farms**: 10-15% of cells (random placement)
- **Mines**: 5-10% of cells (random placement)
- **Markets**: 2-3 market cells per region (fixed locations, e.g., center of each region)
- **Plains**: Rest of cells

**Rationale:**
- Ensures resources exist for producers
- Markets provide trading hubs
- Realistic distribution

---

### Decision 8: Price Update Sensitivity (alpha)

**Decision:** `alpha = 0.1` (10% price adjustment per tick)

**Rationale:**
- Not too sensitive (avoids wild price swings)
- Not too slow (prices respond to market conditions)
- Can tune later based on simulation behavior

**Formula:**
```
new_price = old_price * (1 + alpha * (demand - supply) / max(supply, 1))
```

---

### Decision 9: Health & Consumption Rates

**Decision:**
- **Health decay**: -1 per tick if no food consumed
- **Food consumption**: 1 unit per tick to maintain health
- **Health recovery**: +1 per tick if food consumed (max 100)
- **Death threshold**: Health ≤ 0

**Rationale:**
- Simple, predictable mechanics
- Agents must actively seek food
- Creates survival pressure

---

### Decision 10: Production Rules

**Decision:**
- **Producer (Ore → Tools)**: 
  - Must be adjacent to a mine cell
  - Consumes 2 Ore → produces 1 Tool
  - Takes 1 tick
- **Producer (Food)**: 
  - Must be adjacent to a farm cell
  - Produces 1 Food per tick (no input needed, just location)

**Rationale:**
- Location-based production (realistic)
- Simple conversion ratios
- Creates spatial competition for good spots

---

## Summary Table

| Decision | Choice | Phase 1 Value |
|----------|--------|--------------|
| Action Space | Fixed quantity | 1 unit per action |
| Tick Duration | As-fast-as-possible | No sleep (configurable) |
| Agent Init | Hybrid (constrained random) | Producers near resources |
| World Size | Configurable | 30×30 default |
| Number of Goods | 3 goods | Food, Ore, Tools |
| Agent Count | 20-30 total | 10-15C, 5-8P, 3-5T |
| Terrain | Structured | 10-15% farms, 5-10% mines |
| Price Sensitivity | alpha=0.1 | 10% adjustment |
| Health System | Simple decay | -1/tick without food |
| Production | Location-based | Adjacent to resources |

---

## Next Steps

1. ✅ Decisions finalized
2. ⏭️ Create project structure
3. ⏭️ Implement Phase 1 with these decisions
4. ⏭️ Test and validate economic dynamics
5. ⏭️ Iterate on parameters if needed

