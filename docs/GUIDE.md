# User Guide

Complete guide to understanding and using the simulation.

---

## 🚀 Environment Setup

### Activate Virtual Environment

```bash
source venv/bin/activate
```

When active, you'll see `(venv)` in your terminal prompt.

**To deactivate:**
```bash
deactivate
```

**Verify it's working:**
```bash
python --version  # Should show Python 3.12.4
which python      # Should point to venv/bin/python
```

---

## 🎮 How The Simulation Works

### The Big Picture

The simulation is a **mini economy** running in a 2D world:
- **Agents** (people) move around, trade goods, and produce things
- **Market** sets prices based on supply and demand
- **World** has resources (farms, mines) that agents can use
- Everything happens in **ticks** (like turns in a game)

### Starting the Simulation

```python
sim = Simulation(seed=42)
```

**What happens:**
1. **Creates World** (30×30 grid)
   - Randomly places farms (12% of cells)
   - Randomly places mines (8% of cells)
   - Places 2 markets at fixed locations
   - Rest are plains

2. **Creates Market**
   - Starts with prices: food=1.0, ore=1.0, tools=1.0
   - No goods available yet (quantities = 0)

3. **Creates Agents** (22 total)
   - **12 Consumers**: Random placement, need food to survive
   - **6 Producers**: Placed near farms/mines, can produce goods
   - **4 Traders**: Random placement, buy/sell for profit
   
   Each agent starts with:
   - Random wealth: 50-100 coins
   - Health: 100 (max)
   - Random inventory: 0-5 of each good

### Each Tick (What Happens Every Step)

1. **Agents Take Actions**
   - Smart agents use rule-based decisions (see Smart Agents section)
   - Random agents pick random actions

2. **Execute Actions**
   - Movement, trading, production

3. **Update Health**
   - Agents consume food or lose health

4. **Update Production**
   - Producers create goods from resources

5. **Update Market Prices**
   - Prices adjust based on supply/demand

6. **Remove Dead Agents**
   - Agents with health ≤ 0 are removed

### Price Updates

Market adjusts prices based on supply/demand:

```
High demand, low supply → Price goes UP 📈
Low demand, high supply → Price goes DOWN 📉
```

Formula:
```
price_change = 0.1 * (demand - supply) / supply
new_price = old_price * (1 + price_change)
```

---

## 🤖 Smart Agent Decision-Making

Agents now use **rule-based decision-making** instead of random actions!

### DecisionMaker Class

Analyzes each agent's situation and chooses the best action based on:
- Agent state (health, wealth, inventory, position)
- World context (nearby resources, markets, prices)

### Consumer Strategy 🛒

**Priority:**
1. **Buy food** if health < 50 or no food
2. **Move to market** if need food but can't afford it
3. **Sell excess food** if have > 5 food and low wealth
4. **Random movement** (explore)

### Producer Strategy 🏭

**Priority:**
1. **Produce** if near resources (farm → food, mine → tools)
2. **Sell goods** if have excess (food > 3, tools > 2)
3. **Buy ore** if near mine but don't have ore
4. **Move toward resources** if not near any

### Trader Strategy 💰

**Priority:**
1. **Sell goods** if price is high (arbitrage)
2. **Buy goods** if price is low (stock up)
3. **Move to market** if not already there
4. **Random movement** (explore)

### Using Smart Agents

**Default (smart):**
```python
sim.step(use_smart_decisions=True)  # Default
```

**Random (legacy):**
```python
sim.step(use_smart_decisions=False)
```

**Run scripts:**
```bash
python scripts/run_phase1_smart.py  # Smart agents
python scripts/run_phase1.py        # Random agents
python scripts/compare_decisions.py  # Compare both
```

---

## 🧪 Testing

### Running Tests

**Pytest (recommended):**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_world.py

# Run with verbose output
pytest tests/ -v -s
```

**Simple test scripts:**
```bash
python scripts/test_world.py
```

### Writing Tests

**Pytest test structure:**
```python
def test_world_creation():
    """Test world is created correctly."""
    world = World(seed=42)
    assert world.width == 30
    assert world.height == 30
```

**Assertions:**
```python
assert condition, "optional error message"
```

If condition is `True`: test passes  
If condition is `False`: test fails

---

## 🔢 Understanding Seeds

A **seed** is a starting point for random number generation. It makes randomness **reproducible**.

### Why Seeds Matter

**Without seed:**
```python
random.randint(1, 10)  # → 7 (first run)
random.randint(1, 10)  # → 2 (second run) ❌ Different!
```

**With seed:**
```python
random.seed(42)
random.randint(1, 10)  # → 2

random.seed(42)  # Reset
random.randint(1, 10)  # → 2 ✅ Same!
```

### In Our Simulation

```python
sim = Simulation(seed=42)
```

**What it controls:**
- World terrain placement
- Agent starting positions
- Agent actions (if using random)

**Why 42?** It's a reference to "The Hitchhiker's Guide to the Galaxy" (the answer to life, the universe, and everything). But any number works!

**Different seeds = different worlds:**
```python
seed=42   → World A
seed=123  → World B
seed=999  → World C
```

---

## 📊 Running the Simulation

### Available Scripts

**`run_phase1_smart.py`** - Run with smart agents (recommended)
```bash
python scripts/run_phase1_smart.py
```

**`run_phase1.py`** - Run with random agents (legacy)
```bash
python scripts/run_phase1.py
```

**`compare_decisions.py`** - Compare smart vs random
```bash
python scripts/compare_decisions.py
```

**`test_world.py`** - Quick test of World class
```bash
python scripts/test_world.py
```

### Basic Run Output

```
🚀 Starting Phase 1 Simulation with SMART Agents...
World: World(30x30, farms=108, mines=72, markets=2)
Agents: 22

Running 100 ticks...
Tick  10 | Agents: 22 | Wealth: 1688.6 | Prices: food=1.04, ore=0.91
Tick  20 | Agents: 22 | Wealth: 1693.3 | Prices: food=0.94, ore=1.17
...
```

### What to Look For

- **Agent count**: Should decrease slowly (some agents die)
- **Prices**: Should fluctuate based on supply/demand
- **Wealth**: Should change as agents trade
- **Market quantities**: Should increase as producers create goods

### Script Structure

All scripts follow this pattern:
```python
#!/usr/bin/env python3
"""Description of what the script does."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.simulation import Simulation

def main():
    # Script logic here
    pass

if __name__ == "__main__":
    main()
```

---

## 🎯 Next Steps

### Improve Phase 1
- Add visualization (plot price curves)
- Add more tests
- Tune agent decision rules

### Move to Phase 2
- Multi-region support
- Agent migration between regions

### Move to Phase 3
- HTTP services
- Distributed architecture

### Move to Phase 4
- RL integration
- Policy service

### Move to Phase 5
- Visualization dashboard
- Real-time charts

See [DESIGN_DOC.md](DESIGN_DOC.md) for detailed phase plans.

---

## 🐛 Troubleshooting

**Import errors:**
- Make sure virtual environment is activated
- Check that dependencies are installed: `pip install -r requirements.txt`

**Tests fail:**
- Make sure you're in project root
- Check Python version: `python --version` (need 3.10+)

**Simulation crashes:**
- Check seed value (use integer)
- Verify world size is reasonable (30×30 default)

---

## 📚 Additional Resources

- [DESIGN_DOC.md](DESIGN_DOC.md) - Complete system design
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) - Key decisions
- [scripts/README.md](scripts/README.md) - Scripts documentation

