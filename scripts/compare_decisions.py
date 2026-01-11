#!/usr/bin/env python3
"""Compare smart vs random agent decisions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.simulation import Simulation

def run_simulation(use_smart: bool, name: str):
    """Run simulation and return final stats."""
    sim = Simulation(seed=42)
    
    # Run 50 ticks
    for _ in range(50):
        sim.step(use_smart_decisions=use_smart)
    
    state = sim.get_state_summary()
    return {
        "agents": state["num_agents"],
        "wealth": state["total_wealth"],
        "prices": state["prices"]
    }

def main():
    print("🔬 Comparing Smart vs Random Decisions")
    print("=" * 60)
    
    print("\n1️⃣ Running with SMART decisions...")
    smart_stats = run_simulation(True, "Smart")
    
    print("\n2️⃣ Running with RANDOM decisions...")
    random_stats = run_simulation(False, "Random")
    
    print("\n📊 Results Comparison:")
    print("-" * 60)
    print(f"{'Metric':<20} {'Smart':<20} {'Random':<20}")
    print("-" * 60)
    print(f"{'Agents Alive':<20} {smart_stats['agents']:<20} {random_stats['agents']:<20}")
    print(f"{'Total Wealth':<20} {smart_stats['wealth']:<20.1f} {random_stats['wealth']:<20.1f}")
    print(f"{'Food Price':<20} {smart_stats['prices']['food']:<20.2f} {random_stats['prices']['food']:<20.2f}")
    print(f"{'Ore Price':<20} {smart_stats['prices']['ore']:<20.2f} {random_stats['prices']['ore']:<20.2f}")
    print(f"{'Tools Price':<20} {smart_stats['prices']['tools']:<20.2f} {random_stats['prices']['tools']:<20.2f}")
    print("-" * 60)
    
    print("\n💡 Smart agents should:")
    print("   - Have more agents alive (better survival)")
    print("   - Show more stable prices (rational trading)")
    print("   - Have different wealth distribution")

if __name__ == "__main__":
    main()

