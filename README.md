# Distributed Multi-Agent Economy Simulator

A multi-agent simulation system where agents (consumers, producers, traders) interact in a 2D world with dynamic markets and smart decision-making.

## 🚀 Quick Start

### Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Run the Simulation

**🎨 Visualization Dashboard** (Recommended):
```bash
python scripts/run_dashboard.py
```
Then open http://localhost:8050 in your browser!

**Command Line:**
```bash
# Smart agents
python scripts/run_phase1_smart.py

# Random agents
python scripts/run_phase1.py

# Compare both
python scripts/compare_decisions.py
```

## 📋 What It Does

This simulation creates a mini economy where:
- **22 agents** (consumers, producers, traders) move around a 30×30 world
- **Markets** set prices based on supply and demand
- **Agents** make smart decisions (buy food when health low, produce goods, trade for profit)
- **Prices fluctuate** as agents trade and produce
- **Agents can die** if they don't get food

### How It Works

1. **World**: 30×30 grid with farms, mines, markets, and plains
2. **Agents**: Each agent has health, wealth, and inventory
3. **Market**: Prices change based on supply/demand each tick
4. **Decisions**: Agents use rule-based logic to survive and profit
5. **Simulation**: Runs in ticks, updating everything each step

### Example Output

```
Tick  10 | Agents: 22 | Wealth: 1688.6 | Prices: food=1.04, ore=0.91
Tick  20 | Agents: 22 | Wealth: 1693.3 | Prices: food=0.94, ore=1.17
Tick 100 | Agents: 19 | Wealth: 1480.9 | Prices: food=0.42, ore=8.94
```

## 🎮 Using the Dashboard

The dashboard shows:
- **World Map**: See agents moving on the grid
- **Price Charts**: Watch prices change over time
- **Statistics**: Agent count, wealth, health
- **Controls**: Start/Stop/Step buttons

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Quick test
python scripts/test_world.py
```

## 📁 Project Structure

```
multi-agent-simulator/
├── src/core/       # Simulation logic
├── src/dashboard/ # Visualization
├── scripts/        # Run scripts
└── tests/          # Unit tests
```

## ✅ Current Features

- ✅ 2D world with terrain
- ✅ 3 agent types (Consumers, Producers, Traders)
- ✅ Dynamic market pricing
- ✅ Smart agent decision-making
- ✅ Real-time visualization dashboard
- ✅ Full simulation loop

## 🗺️ Future Plans

- ⏭️ RL Integration (agents learn from experience)
- ⏭️ Multi-region support
- ⏭️ HTTP services (distributed architecture)
- ⏭️ Cloud deployment

See [DEVELOPER.md](DEVELOPER.md) for detailed technical documentation.

## 📝 License

MIT
