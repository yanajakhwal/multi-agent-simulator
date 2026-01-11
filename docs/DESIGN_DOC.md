# Design Document: Distributed Multi-Agent Economy Simulator (RL)

**Author:** Yana Jakhwal  
**Status:** Draft → Implementation Ready  
**Last Updated:** December 2025  
**Version:** 1.0

---

## Table of Contents

1. [Problem & Goals](#1-problem--goals)
2. [High-Level Architecture](#2-high-level-architecture)
3. [World & Sharding Design](#3-world--sharding-design)
4. [Agent & Economy Model](#4-agent--economy-model)
5. [RL Design](#5-rl-design)
6. [Service Design & APIs](#6-service-design--apis)
7. [Simulation Loop](#7-simulation-loop)
8. [Implementation Plan](#8-implementation-plan)
9. [Technical Specifications](#9-technical-specifications)
10. [Success Metrics](#10-success-metrics)

---

## 1. Problem & Goals

### 1.1 Problem Statement

We want to simulate a multi-agent economy where:
- **Agents** (consumers, producers, traders) interact in a 2D world
- The world is **sharded into regions**, each handled by an independent service
- An **RL policy** decides agent actions
- A **coordinator** ties everything together and manages cross-region behavior

### 1.2 Primary Goals

1. **Distributed Architecture**: Real multi-service architecture with message passing
2. **RL Integration**: Policy server that learns from agent interactions
3. **Emergent Behavior**: Observe macro-level patterns:
   - Price dynamics across regions
   - Trade flows and arbitrage
   - Agent migration patterns
   - Wealth distribution

### 1.3 Success Criteria

- ✅ Multiple independent services communicate via HTTP
- ✅ RL policy successfully controls agent behavior
- ✅ Observable economic dynamics (price fluctuations, trade patterns)
- ✅ Agents migrate between regions correctly
- ✅ System runs stably for 1000+ ticks

---

## 2. High-Level Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard / UI                           │
│              (Web interface for monitoring)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Coordinator Service                         │
│  • Global tick loop                                          │
│  • Agent registry (agent_id → region_id)                    │
│  • Observation collection                                    │
│  • Action dispatch                                           │
│  • Cross-region migration handling                           │
└──────┬──────────────────────────────┬───────────────────────┘
       │ HTTP                         │ HTTP
       ▼                              ▼
┌──────────────┐              ┌──────────────┐
│  Region A    │              │  Region B    │  ... N regions
│  (x: 0-24)   │              │  (x: 25-49)  │
│              │              │              │
│  • Local     │              │  • Local     │
│    agents    │              │    agents    │
│  • Markets   │              │  • Markets   │
│  • Cells     │              │  • Cells     │
└──────────────┘              └──────────────┘
       │                              │
       └──────────────┬───────────────┘
                      │ HTTP
                      ▼
              ┌──────────────┐
              │ Policy/RL    │
              │   Service    │
              │              │
              │  • Inference │
              │  • Training  │
              └──────────────┘
```

### 2.2 Component Responsibilities

#### Coordinator Service
- Controls global simulation tick
- Maintains global agent registry: `agent_id → region_id`
- Requests observations from all regions
- Calls Policy Service to get actions
- Dispatches actions to regions and processes results
- Handles cross-region migration

#### Region Service (N instances)
- Owns a subset of world cells (a shard)
- Manages local agents (state, inventory, wealth, health)
- Manages local markets (goods, quantities, prices)
- Executes actions (movement, trade, production)
- Detects agents crossing region boundaries

#### Policy (RL) Service
- Hosts RL models (shared policy across agents initially)
- Given a batch of observations, returns a batch of actions
- Optionally trains from trajectories (V2)

#### Dashboard / Monitoring
- Simple web UI or script
- Queries Coordinator (or Regions) for:
  - Price curves over time
  - Total wealth per region
  - Agent count per region
  - Live grid view of world state

---

## 3. World & Sharding Design

### 3.1 World Representation

**Global World**: 2D grid of size `W × H` (default: 30×30, configurable up to 50×50)

**Partitioning**: Vertical slices by x-coordinate
- Region A: `x ∈ [0, 24]` (or configurable boundaries)
- Region B: `x ∈ [25, 49]` (or configurable boundaries)
- Can extend to N regions

**Cell Structure**:
```python
class Cell:
    terrain_type: Literal["plain", "farm", "mine", "market"]
    base_yield: float  # Resource generation potential
    x: int
    y: int
```

**Terrain Distribution** (Phase 1):
- **Farms**: 10-15% of cells (random placement)
- **Mines**: 5-10% of cells (random placement)
- **Markets**: 2-3 market cells per region (fixed locations)
- **Plains**: Remaining cells

**Key Property**: Coordinator doesn't simulate cells directly; each Region owns its subset.

### 3.2 Sharding Strategy

**Phase 1-2**: Simple vertical slices (by x-coordinate)
**Phase 3+**: Can extend to:
- Horizontal slices
- Grid-based sharding (N×M grid)
- Dynamic sharding based on agent density

**Border Handling**:
- Regions detect when agents cross boundaries
- Coordinator handles migration atomically
- Agent state transferred between regions

---

## 4. Agent & Economy Model

### 4.1 Agent Types

**Base Agent Structure**:
```python
class Agent:
    id: str
    type: Literal["consumer", "producer", "trader"]
    x: int
    y: int
    wealth: float
    health: float
    inventory: Dict[str, float]  # {"food": 10, "ore": 5, "tools": 2}
    region_id: str
```

**Agent Types**:

1. **Consumers**
   - Need "food" per tick to maintain health
   - Buy from markets if available
   - Reward: `+1 if health > previous_health`, `-1 if health drops`, `-small_penalty per wealth spent`

2. **Producers**
   - Located near resource cells (farms/mines)
   - Convert resources to goods:
     - **Food Producer**: Adjacent to farm → produces 1 Food/tick
     - **Tool Producer**: Adjacent to mine → consumes 2 Ore → produces 1 Tool
   - Reward: `wealth_t - wealth_{t-1}` (profit)

3. **Traders**
   - Move goods between regions
   - Buy cheap, sell high (arbitrage)
   - Reward: `wealth_t - wealth_{t-1}` (arbitrage profit)

### 4.2 Agent Initialization

**Placement Strategy** (Hybrid):
- **Consumers**: Random placement anywhere
- **Producers**: Random placement within 2 cells of a resource cell (farm or mine)
- **Traders**: Random placement, prefer near region borders or market cells

**Starting Stats**:
- Wealth: Random uniform `[50, 100]`
- Health: `100` (max)
- Inventory: Random small amounts `[0, 5]` of each good

**Phase 1 Agent Count**: 20-30 total
- 10-15 Consumers
- 5-8 Producers
- 3-5 Traders

### 4.3 Market Model (per Region)

**Market State**:
```python
class GoodState:
    quantity: float  # Available supply
    price: float     # Current price per unit

class Market:
    goods: Dict[str, GoodState]  # {"food": GoodState, "ore": ..., "tools": ...}
```

**Price Update Rule** (per tick):
```
demand = units requested to buy
supply = units actually added to market
alpha = 0.1  # Price sensitivity

new_price = old_price * (1 + alpha * (demand - supply) / max(supply, 1))
```

**Market Clearing**:
- Buy orders execute if agent has sufficient wealth
- Sell orders execute if agent has sufficient inventory
- Orders processed sequentially within a tick
- Price updates after all transactions

### 4.4 Goods & Production

**Goods** (3 total):
1. **Food**: Consumed by all agents (health maintenance)
2. **Ore**: Raw resource, mined from mine cells
3. **Tools**: Produced from Ore, used for production efficiency (optional bonus)

**Production Rules**:
- **Food Producer**: Must be adjacent to farm cell → produces 1 Food/tick (no input)
- **Tool Producer**: Must be adjacent to mine cell → consumes 2 Ore → produces 1 Tool/tick

**Consumption Rules**:
- All agents consume 1 Food/tick to maintain health
- If no food consumed: health decreases by 1/tick
- If food consumed: health increases by 1/tick (max 100)
- Death: Health ≤ 0

---

## 5. RL Design

### 5.1 Observation Space

**Per-agent observation** (flattened vector):

```python
obs = {
    # Agent state
    "wealth": float,              # Normalized [0, 1]
    "health": float,               # Normalized [0, 1]
    "inventory_food": float,      # Normalized
    "inventory_ore": float,       # Normalized
    "inventory_tools": float,     # Normalized
    
    # Market state (local region)
    "local_price_food": float,    # Normalized
    "local_price_ore": float,     # Normalized
    "local_price_tools": float,   # Normalized
    "local_quantity_food": float, # Normalized
    "local_quantity_ore": float,  # Normalized
    "local_quantity_tools": float,# Normalized
    
    # Spatial context
    "region_id": int,             # One-hot encoded or integer
    "dist_to_border": float,      # Normalized distance to nearest region border
    "local_agent_density": float, # Agents in radius / max_agents_in_radius
    
    # Terrain context (optional)
    "cell_type": int,             # One-hot: plain, farm, mine, market
    "adjacent_resources": int,    # Count of adjacent resource cells
}
```

**Normalization Strategy**:
- Continuous features: Min-max normalization or standardization
- Use running statistics or fixed bounds (e.g., wealth: [0, 1000] → [0, 1])

**Shared Policy**: Initially, all agents use the same policy network. Can extend to type-specific policies later.

### 5.2 Action Space

**Discrete action space** (9 actions per agent):

```python
ACTIONS = {
    0: "STAY",
    1: "MOVE_NORTH",
    2: "MOVE_SOUTH",
    3: "MOVE_EAST",
    4: "MOVE_WEST",
    5: "BUY_FOOD",      # Buy 1 unit of food
    6: "SELL_FOOD",     # Sell 1 unit of food
    7: "BUY_ORE",       # Buy 1 unit of ore
    8: "SELL_ORE",      # Sell 1 unit of ore
    9: "BUY_TOOLS",     # Buy 1 unit of tools
    10: "SELL_TOOLS",   # Sell 1 unit of tools
    11: "PRODUCE",      # Produce goods (if producer, location-dependent)
}
```

**Action Semantics**:
- **Fixed quantity**: Each buy/sell action operates on exactly 1 unit
- **Movement**: Moves agent 1 cell in specified direction (if valid)
- **Produce**: Only valid if agent is producer and adjacent to required resource
- **Invalid actions**: Fail gracefully (no-op or small penalty)

### 5.3 Reward Design

**Per-step reward** (depends on agent type):

**Consumers**:
```python
reward = (
    +1.0 if health > previous_health else 0.0
    -1.0 if health < previous_health
    -0.1 * wealth_spent  # Small penalty for spending
)
```

**Producers/Traders**:
```python
reward = wealth_t - wealth_{t-1}  # Profit-based
```

**Global Shaping**:
- `-10.0` if agent dies (health ≤ 0)
- `-0.01` per time step (optional, encourages efficiency)

**Reward Normalization**: Consider normalizing rewards to `[-1, 1]` range for training stability.

### 5.4 RL Training Flow

**Phase 1**: Scripted policies (non-RL) to validate environment

**Phase 4**: RL integration

**Training Pipeline**:
1. Coordinator gathers transitions: `(obs_t, action_t, reward_t, obs_{t+1})` for each agent
2. Batches sent periodically to Policy Service for training (background thread)
3. Policy Service updates model weights
4. Inference uses latest model

**Implementation**:
- Framework: PyTorch
- Algorithm: DQN or PPO (start with DQN for simplicity)
- Single policy network initially
- Experience replay buffer (for DQN)

**Training Schedule**:
- Collect transitions for N ticks (e.g., 100)
- Send batch to Policy Service
- Policy Service trains for K epochs
- Update model weights
- Continue simulation

---

## 6. Service Design & APIs

### 6.1 Technology Stack

- **HTTP Framework**: FastAPI (async-ready, type hints, OpenAPI docs)
- **Data Validation**: Pydantic models
- **RL Framework**: PyTorch
- **Visualization**: Plotly/Dash or simple HTML+JS
- **Containerization**: Docker + docker-compose

### 6.2 Region Service API

**Base URL**: `http://localhost:8001` (Region A), `http://localhost:8002` (Region B), etc.

#### `POST /step`
Execute one simulation step for agents in this region.

**Request**:
```json
{
  "tick": 123,
  "actions": [
    {"agent_id": "a1", "action_id": 5},
    {"agent_id": "a2", "action_id": 1}
  ]
}
```

**Response**:
```json
{
  "agent_states": [
    {
      "agent_id": "a1",
      "x": 10,
      "y": 15,
      "wealth": 75.5,
      "health": 95,
      "inventory": {"food": 3, "ore": 1, "tools": 0}
    },
    ...
  ],
  "border_crossings": [
    {
      "agent_id": "a7",
      "from_region": "A",
      "to_global_coords": [26, 10],
      "agent_state": {...}
    }
  ],
  "market_delta": {
    "food": {"demand": 5, "supply": 2},
    "ore": {"demand": 0, "supply": 3},
    "tools": {"demand": 1, "supply": 0}
  },
  "rewards": [
    {"agent_id": "a1", "reward": 0.5},
    {"agent_id": "a2", "reward": -0.1}
  ],
  "deaths": ["a3"]  // Agents that died this tick
}
```

#### `GET /observations`
Get current per-agent observation vectors for this region.

**Response**:
```json
{
  "observations": [
    {
      "agent_id": "a1",
      "obs": [0.2, 0.3, 0.1, ...]  // Flattened observation vector
    },
    ...
  ]
}
```

#### `POST /add_agent`
Add a migrated or new agent to this region.

**Request**:
```json
{
  "agent": {
    "agent_id": "a7",
    "type": "consumer",
    "x": 26,
    "y": 10,
    "wealth": 80,
    "health": 100,
    "inventory": {"food": 5, "ore": 0, "tools": 0}
  }
}
```

#### `POST /remove_agent`
Remove an agent from this region (migration or death).

**Request**:
```json
{
  "agent_id": "a7"
}
```

#### `GET /market_state`
Get current market state for dashboard/metrics.

**Response**:
```json
{
  "goods": {
    "food": {"quantity": 50, "price": 2.5},
    "ore": {"quantity": 30, "price": 5.0},
    "tools": {"quantity": 10, "price": 15.0}
  }
}
```

### 6.3 Coordinator Service API

**Base URL**: `http://localhost:8000`

#### `GET /metrics/global`
Get global simulation metrics.

**Response**:
```json
{
  "tick": 123,
  "total_agents": 25,
  "agents_per_region": {
    "A": 12,
    "B": 13
  },
  "total_wealth": 2500.0,
  "wealth_per_region": {
    "A": 1200.0,
    "B": 1300.0
  },
  "avg_prices": {
    "A": {"food": 2.5, "ore": 5.0, "tools": 15.0},
    "B": {"food": 2.8, "ore": 4.8, "tools": 14.5}
  }
}
```

#### `GET /state/agents`
Get state of all agents (for dashboard).

**Response**:
```json
{
  "agents": [
    {
      "agent_id": "a1",
      "region_id": "A",
      "type": "consumer",
      "x": 10,
      "y": 15,
      "wealth": 75.5,
      "health": 95
    },
    ...
  ]
}
```

#### `GET /state/regions`
Get state of all regions.

**Response**:
```json
{
  "regions": [
    {
      "region_id": "A",
      "bounds": {"x_min": 0, "x_max": 24, "y_min": 0, "y_max": 29},
      "agent_count": 12,
      "market_state": {...}
    },
    ...
  ]
}
```

#### `POST /start`
Start the simulation (begin tick loop).

**Request**:
```json
{
  "num_ticks": 1000,  // Optional: run for N ticks then stop
  "tick_rate": null   // Optional: seconds per tick (null = as-fast-as-possible)
}
```

#### `POST /stop`
Stop the simulation.

### 6.4 Policy (RL) Service API

**Base URL**: `http://localhost:8003`

#### `POST /act`
Get actions for a batch of observations.

**Request**:
```json
{
  "agents": [
    {
      "agent_id": "a1",
      "obs": [0.2, 0.3, 0.1, ...]  // Flattened observation vector
    },
    {
      "agent_id": "a2",
      "obs": [0.1, 0.4, 0.2, ...]
    }
  ]
}
```

**Response**:
```json
{
  "actions": [
    {"agent_id": "a1", "action_id": 5},
    {"agent_id": "a2", "action_id": 1}
  ]
}
```

#### `POST /train` (Phase 4)
Train the policy on a batch of transitions.

**Request**:
```json
{
  "transitions": [
    {
      "agent_id": "a1",
      "obs_t": [0.2, 0.3, ...],
      "action_t": 5,
      "reward_t": 0.5,
      "obs_t_next": [0.25, 0.35, ...],
      "done": false
    },
    ...
  ]
}
```

**Response**:
```json
{
  "loss": 0.123,
  "metrics": {
    "avg_reward": 0.45,
    "policy_entropy": 2.1
  }
}
```

---

## 7. Simulation Loop

### 7.1 End-to-End Tick Flow

**Per tick**:

1. **Coordinator → Regions**: `GET /observations`
   - Collect all per-agent observations from all regions

2. **Coordinator → Policy Server**: `POST /act`
   - Send all observations as batch
   - Receive actions for all agents

3. **Coordinator**: Group actions by region
   ```python
   region_actions = {
       "RegionA": [action for agent in RegionA],
       "RegionB": [action for agent in RegionB],
   }
   ```

4. **Coordinator → Regions**: `POST /step` (parallel)
   - Send actions to each region
   - Regions execute actions, update markets, compute rewards

5. **Regions → Coordinator**: Return updated states
   - Agent states, rewards, border crossings, deaths

6. **Coordinator**: Process results
   - Update `agent_registry` for migrated agents
   - Call `/add_agent`/`/remove_agent` for migrations
   - Store transitions: `(obs_t, action_t, reward_t, obs_{t+1})`

7. **Coordinator → Policy Server** (periodic): `POST /train`
   - Send accumulated transitions for training
   - Policy updates model weights

8. **Dashboard**: Polls coordinator/regions
   - Render world state, metrics, charts

### 7.2 Error Handling

**Phase 1 Simplifications**:
- Assume all services respond (no network failures)
- Blocking HTTP calls (no async needed initially)
- Single-threaded coordinator

**Phase 3+ Enhancements**:
- Retry logic for failed requests
- Timeout handling
- Graceful degradation (skip region if unresponsive)
- Async HTTP calls for better performance

---

## 8. Implementation Plan

### Phase 1 – Local Single-Process Prototype ✅ **START HERE**

**Goal**: Get core economic dynamics working in a single Python script.

**Tasks**:
1. ✅ Design decisions finalized
2. ⏭️ Implement `World` class with grid and cells
3. ⏭️ Implement `Agent` base class and subtypes (Consumer, Producer, Trader)
4. ⏭️ Implement `Market` class with price update logic
5. ⏭️ Implement single-tick execution:
   - Collect actions (scripted for now)
   - Execute actions (movement, trade, production)
   - Update markets & prices
   - Compute rewards
   - Update agent states
6. ⏭️ Implement multi-tick loop
7. ⏭️ Add logging/metrics (prices, wealth, agent count over time)
8. ⏭️ Validate: Run 100+ ticks, verify no crashes, check economic dynamics

**Success Criteria**:
- Agents can move, trade, produce
- Prices fluctuate based on supply/demand
- Agents can die and be removed
- 100+ ticks run without crashes
- Simple metrics logged

**Estimated Time**: 1-2 weeks

---

### Phase 2 – Multi-Region, Single Process

**Goal**: Refactor to support multiple regions in same process.

**Tasks**:
1. Refactor code to have `Region` objects
2. Implement sharding logic (vertical slices)
3. Implement `Coordinator` class (same process, but clear interfaces)
4. Implement border crossing detection
5. Implement agent migration between regions
6. Validate: Agents migrate correctly, regions maintain correct state

**Success Criteria**:
- Multiple regions exist and own correct cells
- Agents migrate between regions correctly
- Coordinator manages global state correctly

**Estimated Time**: 1 week

---

### Phase 3 – Multi-Service Split

**Goal**: Split into separate HTTP services.

**Tasks**:
1. Convert `Region` → FastAPI service (`region_service.py`)
2. Convert `Coordinator` → FastAPI service (`coordinator_service.py`)
3. Replace direct function calls with HTTP calls
4. Implement all API endpoints
5. Test: Run services in separate terminals, verify communication
6. Add docker-compose for easy orchestration

**Success Criteria**:
- All services run independently
- HTTP communication works correctly
- Simulation runs end-to-end via HTTP

**Estimated Time**: 1-2 weeks

---

### Phase 4 – Policy Service & RL Integration

**Goal**: Add RL policy server and integrate with simulation.

**Tasks**:
1. Implement `Policy Service` with FastAPI
2. Implement `POST /act` with random policy first
3. Implement observation space builder
4. Implement action space definitions
5. Implement reward computation
6. Integrate PyTorch + simple DQN/PPO
7. Implement `POST /train` endpoint
8. Connect Coordinator → Policy Service for inference
9. Connect Coordinator → Policy Service for training (periodic)
10. Validate: RL agents learn and improve behavior

**Success Criteria**:
- Policy Service returns actions for observations
- RL model trains on collected transitions
- Agent behavior improves over time (optional, for V2)

**Estimated Time**: 2-3 weeks

---

### Phase 5 – Visualization & Polish

**Goal**: Add dashboard and production-ready features.

**Tasks**:
1. Implement simple dashboard (Flask/FastAPI + HTML/JS)
2. Add real-time price charts
3. Add agent count/wealth visualizations
4. Add simple grid view of world
5. Add logging infrastructure
6. Add error handling and retries
7. Add monitoring/metrics (optional: Prometheus)
8. Write README with setup instructions
9. Add unit tests
10. Containerize with Docker

**Success Criteria**:
- Dashboard displays simulation state
- System is easy to run (`docker-compose up`)
- Documentation is complete

**Estimated Time**: 1-2 weeks

---

## 9. Technical Specifications

### 9.1 Data Structures

**Core Classes**:
```python
# World & Cells
class Cell:
    terrain_type: Literal["plain", "farm", "mine", "market"]
    base_yield: float
    x: int
    y: int

class World:
    width: int
    height: int
    cells: List[List[Cell]]

# Agents
class Agent:
    id: str
    type: Literal["consumer", "producer", "trader"]
    x: int
    y: int
    wealth: float
    health: float
    inventory: Dict[str, float]
    region_id: str

# Markets
class GoodState:
    quantity: float
    price: float

class Market:
    goods: Dict[str, GoodState]
```

### 9.2 Configuration

**Phase 1 Config** (hardcoded or config file):
```python
WORLD_WIDTH = 30
WORLD_HEIGHT = 30
NUM_CONSUMERS = 12
NUM_PRODUCERS = 6
NUM_TRADERS = 4
PRICE_ALPHA = 0.1
HEALTH_DECAY_RATE = 1
FOOD_CONSUMPTION_RATE = 1
```

### 9.3 File Structure

```
multi-agent-simulator/
├── README.md
├── DESIGN_DOC.md
├── DESIGN_DECISIONS.md
├── requirements.txt
├── docker-compose.yml
│
├── src/
│   ├── core/
│   │   ├── world.py
│   │   ├── agent.py
│   │   ├── market.py
│   │   └── economy.py
│   ├── region/
│   │   ├── region.py
│   │   └── sharding.py
│   ├── coordinator/
│   │   ├── coordinator.py
│   │   └── registry.py
│   ├── rl/
│   │   ├── observation.py
│   │   ├── action.py
│   │   ├── reward.py
│   │   └── models/
│   ├── services/
│   │   ├── region_service.py
│   │   ├── coordinator_service.py
│   │   └── policy_service.py
│   └── dashboard/
│       └── app.py
│
├── tests/
└── scripts/
```

---

## 10. Success Metrics

### 10.1 Functional Metrics

- ✅ Simulation runs for 1000+ ticks without crashes
- ✅ Agents migrate between regions correctly
- ✅ Prices respond to supply/demand
- ✅ RL policy successfully controls agents
- ✅ Economic dynamics emerge (trade flows, price differences)

### 10.2 Performance Metrics

- **Tick Rate**: Target 10-100 ticks/second (Phase 1)
- **Latency**: HTTP calls < 100ms (Phase 3)
- **Scalability**: Support 100+ agents across 3+ regions (Phase 3)

### 10.3 Quality Metrics

- **Code Coverage**: > 70% (Phase 5)
- **Documentation**: Complete README + API docs (Phase 5)
- **Reliability**: Handles edge cases gracefully (Phase 5)

---

## Appendix A: Key Design Decisions Summary

See `DESIGN_DECISIONS.md` for detailed rationale.

| Decision | Choice |
|----------|--------|
| Action Space | Fixed quantity (1 unit per action) |
| Tick Duration | As-fast-as-possible (configurable) |
| Agent Init | Hybrid (constrained random) |
| World Size | Configurable (30×30 default) |
| Number of Goods | 3 goods (Food, Ore, Tools) |
| Agent Count | 20-30 total |
| Price Sensitivity | alpha = 0.1 |

---

## Appendix B: Future Enhancements (Post-MVP)

1. **Advanced RL**:
   - Multi-agent RL algorithms (MADDPG, MAPPO)
   - Hierarchical policies
   - Transfer learning across regions

2. **Advanced Economics**:
   - Multiple currencies
   - Contracts and agreements
   - Complex production chains
   - Banking/loans

3. **Scalability**:
   - Horizontal scaling (more region instances)
   - Database persistence
   - Event sourcing for replay

4. **Visualization**:
   - 3D visualization
   - Agent trajectory replay
   - Interactive parameter tuning

---

**End of Design Document**

