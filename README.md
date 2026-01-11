# Distributed Multi-Agent Economy Simulator (RL)

A distributed multi-agent simulation system where agents (consumers, producers, traders) interact in a 2D world, controlled by reinforcement learning policies.

## 📋 Overview

This project simulates an economy with:
- **Agents** that move, trade, and produce goods
- **Markets** with dynamic pricing based on supply/demand
- **RL policies** that control agent behavior (Phase 4)
- **Distributed architecture** with sharded regions (Phase 3)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

**Virtual environment is already created!** Just activate it:

```bash
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when it's active.

**Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

### Run the Simulation

**With smart agents** (recommended):
```bash
python scripts/run_phase1_smart.py
```

**With random agents** (legacy):
```bash
python scripts/run_phase1.py
```

**Compare both**:
```bash
python scripts/compare_decisions.py
```

## 📁 Project Structure

```
multi-agent-simulator/
├── src/
│   ├── core/          # Core game logic (Phase 1) ✅
│   ├── region/        # Region logic (Phase 2)
│   ├── coordinator/   # Coordinator (Phase 2-3)
│   ├── rl/            # RL components (Phase 4)
│   ├── services/      # HTTP services (Phase 3-4)
│   └── dashboard/     # Visualization (Phase 5)
├── tests/             # Unit tests ✅
├── scripts/           # Run scripts ✅
└── docs/              # Documentation
```

## ✅ Current Status

**Phase 1: Complete!** ✅

- ✅ World with terrain (farms, mines, markets)
- ✅ 3 agent types (Consumers, Producers, Traders)
- ✅ Market with dynamic pricing
- ✅ Smart rule-based decision-making
- ✅ Full simulation loop
- ✅ Testing infrastructure

**What works:**
- Agents move, trade, and produce goods
- Prices fluctuate based on supply/demand
- Agents make smart decisions (buy food when health low, etc.)
- Simulation runs 100+ ticks stably

## 🗺️ Implementation Phases

- **Phase 1**: Single-process prototype ✅ **DONE**
- **Phase 2**: Multi-region, single process
- **Phase 3**: Multi-service split (HTTP)
- **Phase 4**: RL integration
- **Phase 5**: Visualization & polish

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Quick test
python scripts/test_world.py
```

## 📚 Documentation

- **[GUIDE.md](GUIDE.md)** - How it works, testing, smart agents, setup
- **[DESIGN_DOC.md](DESIGN_DOC.md)** - Complete system design
- **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** - Key implementation decisions

## 📝 License

MIT
