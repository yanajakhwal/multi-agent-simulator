# Distributed Multi-Agent Economy Simulator (RL)

A distributed multi-agent simulation system where agents (consumers, producers, traders) interact in a 2D world, controlled by reinforcement learning policies.

## 📋 Overview

This project simulates an economy with:
- **Agents** that move, trade, and produce goods
- **Markets** with dynamic pricing based on supply/demand
- **RL policies** that control agent behavior
- **Distributed architecture** with sharded regions

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Phase 1 prototype
python scripts/run_phase1.py
```

## 📁 Project Structure

```
multi-agent-simulator/
├── src/
│   ├── core/          # Core game logic (Phase 1)
│   ├── region/        # Region logic (Phase 2)
│   ├── coordinator/   # Coordinator (Phase 2-3)
│   ├── rl/            # RL components (Phase 4)
│   ├── services/      # HTTP services (Phase 3-4)
│   └── dashboard/     # Visualization (Phase 5)
├── tests/             # Unit tests
└── scripts/           # Run scripts
```

## 📚 Documentation

- [Design Document](DESIGN_DOC.md) - Complete system design
- [Design Decisions](DESIGN_DECISIONS.md) - Key implementation decisions

## 🗺️ Implementation Phases

- **Phase 1**: Single-process prototype (current)
- **Phase 2**: Multi-region, single process
- **Phase 3**: Multi-service split (HTTP)
- **Phase 4**: RL integration
- **Phase 5**: Visualization & polish

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

MIT

