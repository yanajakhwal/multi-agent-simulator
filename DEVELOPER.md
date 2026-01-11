# Developer Documentation

Complete technical documentation for developers working on this project.

**Author:** Yana Jakhwal  
**Last Updated:** December 2025

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Decisions](#design-decisions)
3. [Implementation Details](#implementation-details)
4. [Technology Stack](#technology-stack)
5. [Roadmap](#roadmap)
6. [API Specifications](#api-specifications)
7. [Testing](#testing)

---

## Architecture Overview

### System Components

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
│  • Local     │              │  • Local     │
│    agents    │              │    agents    │
│  • Markets   │              │  • Markets   │
└──────────────┘              └──────────────┘
       │                              │
       └──────────────┬───────────────┘
                      │ HTTP
                      ▼
              ┌──────────────┐
              │ Policy/RL    │
              │   Service    │
              │  • Inference │
              │  • Training  │
              └──────────────┘
```

### Current Implementation (Phase 1)

- **Single Process**: All components in one Python process
- **World**: 30×30 grid with terrain
- **Agents**: 22 agents (12 consumers, 6 producers, 4 traders)
- **Market**: Dynamic pricing based on supply/demand
- **Decision Making**: Rule-based (smart agents)
- **Visualization**: Dash dashboard

---

## Design Decisions

### Action Space
**Decision**: Fixed quantity per action (1 unit per action)

**Rationale**: Simplest to implement, smaller action space for RL, clear semantics

**Actions**:
- 0: Stay
- 1-4: Move (N, S, E, W)
- 5-6: Buy/Sell food
- 7-8: Buy/Sell ore
- 9-10: Buy/Sell tools
- 11: Produce

### Tick Duration
**Decision**: As-fast-as-possible (configurable)

**Rationale**: Faster iteration, can add sleep for visualization

### Agent Initialization
**Decision**: Hybrid (constrained random)

- Consumers: Random placement
- Producers: Near resources (within 2 cells)
- Traders: Random, prefer markets

**Starting Stats**:
- Wealth: 50-100 (random)
- Health: 100 (max)
- Inventory: 0-5 of each good (random)

### World Size
**Decision**: Configurable (default 30×30)

**Rationale**: Good balance, easy to visualize, can scale up

### Number of Goods
**Decision**: 3 goods (Food, Ore, Tools)

**Rationale**: Creates production chain, not too simple/complex

### Price Update Sensitivity
**Decision**: alpha = 0.1 (10% adjustment)

**Formula**:
```
new_price = old_price * (1 + alpha * (demand - supply) / max(supply, 1))
```

### Health System
**Decision**: Simple decay/recovery

- Health decay: -1/tick without food
- Health recovery: +1/tick with food
- Death: Health ≤ 0

### Production Rules
**Decision**: Location-based

- Food Producer: Adjacent to farm → produces 1 Food/tick
- Tool Producer: Adjacent to mine → consumes 2 Ore → produces 1 Tool/tick

---

## Implementation Details

### Core Classes

**World** (`src/core/world.py`):
- Manages 2D grid of cells
- Terrain generation (farms, mines, markets)
- Cell access and validation
- Resource detection

**Agent** (`src/core/agent.py`):
- Base Agent class
- Consumer, Producer, Trader subclasses
- Inventory, wealth, health management
- Movement system

**Market** (`src/core/market.py`):
- Tracks goods (food, ore, tools)
- Dynamic price updates
- Buy/sell operations
- Supply/demand tracking

**Simulation** (`src/core/simulation.py`):
- Main simulation loop
- Tick-based execution
- Action execution
- Health/consumption updates
- Metrics tracking

**DecisionMaker** (`src/core/decision_maker.py`):
- Rule-based decision logic
- Different strategies per agent type
- Context-aware decisions

### Data Structures

```python
class Cell:
    x: int
    y: int
    terrain_type: Literal["plain", "farm", "mine", "market"]
    base_yield: float

class Agent:
    id: str
    type: Literal["consumer", "producer", "trader"]
    x: int
    y: int
    wealth: float
    health: float
    inventory: Dict[str, float]

class Market:
    goods: Dict[str, GoodState]  # {"food": GoodState, ...}
```

---

## Technology Stack

### Current Stack

- **Python 3.12** - Core language
- **NumPy** - Numerical operations
- **Pydantic** - Data validation
- **Dash/Plotly** - Visualization
- **PyTorch** - RL (installed, not yet used)
- **FastAPI** - HTTP services (installed, not yet used)
- **pytest** - Testing

### Future Stack (Planned)

**Phase 2-3:**
- **FastAPI** - HTTP services
- **PostgreSQL** - Database
- **Redis** - Cache & real-time

**Phase 4:**
- **PyTorch** - RL models
- **Gymnasium** - RL environments

**Phase 5:**
- **Docker** - Containerization
- **Cloud Platform** - Deployment

### Why Python?

- ✅ Already working
- ✅ Fast enough for current scale
- ✅ Better for ML/RL (PyTorch)
- ✅ Faster development
- ✅ Can add C++ extensions later if needed

---

## Roadmap

### Phase 1: Single-Process Prototype ✅ **COMPLETE**

- ✅ World with terrain
- ✅ Agent system (3 types)
- ✅ Market with dynamic pricing
- ✅ Smart decision-making
- ✅ Visualization dashboard
- ✅ Testing infrastructure

### Phase 2: RL Integration ⏭️ **NEXT**

**Goal**: Add machine learning so agents learn from experience

**Tasks**:
- [ ] Design observation space
- [ ] Design action space
- [ ] Implement reward function
- [ ] Create policy network (PyTorch)
- [ ] Build Policy Service (FastAPI)
- [ ] Implement training loop
- [ ] Connect to simulation
- [ ] Test learning

**Timeline**: 2-3 weeks

### Phase 3: Multi-Region ⏭️

**Goal**: Split world into regions, support agent migration

**Tasks**:
- [ ] Create Region class
- [ ] Implement sharding logic
- [ ] Create Coordinator class
- [ ] Handle border crossings
- [ ] Agent migration logic

**Timeline**: 1 week

### Phase 4: HTTP Services ⏭️

**Goal**: Convert to distributed architecture

**Tasks**:
- [ ] Convert Region → FastAPI service
- [ ] Convert Coordinator → FastAPI service
- [ ] Implement HTTP endpoints
- [ ] Replace function calls with HTTP
- [ ] Docker setup

**Timeline**: 1-2 weeks

### Phase 5: Deployment ⏭️

**Goal**: Make it accessible to others

**Tasks**:
- [ ] Create Dockerfile
- [ ] Docker Compose setup
- [ ] Deploy to cloud
- [ ] Set up domain/URL
- [ ] Documentation

**Timeline**: 1 week

---

## API Specifications

### Region Service (Future)

**POST /step**
```json
{
  "tick": 123,
  "actions": [
    {"agent_id": "a1", "action_id": 5}
  ]
}
```

**GET /observations**
```json
{
  "observations": [
    {"agent_id": "a1", "obs": [0.2, 0.3, ...]}
  ]
}
```

### Coordinator Service (Future)

**GET /metrics/global**
```json
{
  "tick": 123,
  "total_agents": 25,
  "total_wealth": 2500.0,
  "avg_prices": {...}
}
```

### Policy Service (Future)

**POST /act**
```json
{
  "agents": [
    {"agent_id": "a1", "obs": [0.2, 0.3, ...]}
  ]
}
```

**POST /train**
```json
{
  "transitions": [
    {
      "agent_id": "a1",
      "obs_t": [...],
      "action_t": 5,
      "reward_t": 0.5,
      "obs_t_next": [...]
    }
  ]
}
```

---

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_world.py

# With coverage
pytest --cov=src tests/
```

### Test Structure

- `tests/test_world.py` - World class tests (9 tests)
- `tests/conftest.py` - Pytest configuration

### Writing Tests

```python
def test_world_creation():
    """Test world is created correctly."""
    world = World(seed=42)
    assert world.width == 30
    assert world.height == 30
```

---

## Code Organization

```
src/
├── core/          # Core simulation logic
│   ├── world.py
│   ├── agent.py
│   ├── market.py
│   ├── simulation.py
│   ├── decision_maker.py
│   └── config.py
├── dashboard/     # Visualization
│   └── app.py
├── region/        # Region logic (Phase 2)
├── coordinator/   # Coordinator (Phase 2-3)
├── rl/            # RL components (Phase 4)
└── services/      # HTTP services (Phase 3-4)
```

---

## Configuration

All constants in `src/core/config.py`:

- `WORLD_WIDTH = 30`
- `WORLD_HEIGHT = 30`
- `NUM_CONSUMERS = 12`
- `NUM_PRODUCERS = 6`
- `NUM_TRADERS = 4`
- `PRICE_ALPHA = 0.1`
- `MAX_HEALTH = 100`
- `GOODS = ["food", "ore", "tools"]`

---

## Development Workflow

### Running Locally

```bash
# Activate environment
source venv/bin/activate

# Run dashboard
python scripts/run_dashboard.py

# Run simulation
python scripts/run_phase1_smart.py

# Run tests
pytest tests/ -v
```

### Adding Features

1. Create feature branch
2. Write tests first
3. Implement feature
4. Run tests
5. Update documentation

---

## Performance Considerations

### Current Performance
- 22 agents, 30×30 world
- ~0.1-1 second per 100 ticks
- Python is fast enough for current scale

### Optimization Opportunities
- Use NumPy for array operations
- Profile to find bottlenecks
- Add C++ extensions if needed
- Parallelize region processing (Phase 3)

---

## Future Enhancements

### Short Term
- RL integration
- Multi-region support
- HTTP services

### Long Term
- Advanced RL algorithms (MADDPG, MAPPO)
- Multiple currencies
- Complex production chains
- Horizontal scaling
- Database persistence
- Event sourcing

---

## Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

### Pull Request Process
1. Create feature branch
2. Write tests
3. Implement feature
4. Update documentation
5. Submit PR

---

## Resources

- [PyTorch Documentation](https://pytorch.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dash Documentation](https://dash.plotly.com/)
- [Design Document](docs/DESIGN_DOC.md) - Detailed design (if needed)

---

**For user documentation, see [README.md](README.md)**

