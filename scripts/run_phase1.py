#!/usr/bin/env python3
"""Run Phase 1 simulation - single process prototype."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.simulation import Simulation

def main():
    print("🚀 Starting Phase 1 Simulation (Random Actions)...")
    print("=" * 60)
    
    # Create simulation
    sim = Simulation(seed=42)
    
    print(f"World: {sim.world}")
    print(f"Agents: {len(sim.agents)}")
    print(f"Market: {sim.market}")
    print()
    print("🎲 Agents use RANDOM actions (legacy mode)")
    print("   For smart agents, use: python scripts/run_phase1_smart.py")
    print()
    
    # Run simulation for 100 ticks
    num_ticks = 100
    
    print(f"Running {num_ticks} ticks...")
    print("-" * 60)
    
    for i in range(num_ticks):
        sim.step(use_smart_decisions=False)  # Use random actions
        
        # Print summary every 10 ticks
        if (i + 1) % 10 == 0:
            state = sim.get_state_summary()
            print(f"Tick {state['tick']:3d} | "
                  f"Agents: {state['num_agents']:2d} | "
                  f"Wealth: {state['total_wealth']:7.1f} | "
                  f"Prices: food={state['prices']['food']:.2f}, "
                  f"ore={state['prices']['ore']:.2f}, "
                  f"tools={state['prices']['tools']:.2f}")
    
    print("-" * 60)
    print("\n✅ Simulation completed!")
    
    # Final summary
    final_state = sim.get_state_summary()
    print(f"\nFinal State:")
    print(f"  Agents: {final_state['num_agents']}")
    print(f"  Total Wealth: {final_state['total_wealth']:.1f}")
    print(f"  Prices:")
    for good, price in final_state['prices'].items():
        print(f"    {good}: {price:.2f}")
    print(f"  Market Quantities:")
    for good, qty in final_state['market_quantities'].items():
        print(f"    {good}: {qty:.1f}")

if __name__ == "__main__":
    main()

