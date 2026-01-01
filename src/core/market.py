"""
Market class for managing goods, prices, and supply/demand.

Markets update prices based on supply and demand each tick.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field

from .config import GOODS, PRICE_ALPHA


@dataclass
class GoodState:
    """State of a single good in the market."""
    
    quantity: float = 0.0  # Available supply
    price: float = 1.0  # Current price per unit
    
    def __repr__(self) -> str:
        return f"GoodState(qty={self.quantity:.1f}, price={self.price:.2f})"


class Market:
    """Market that tracks goods, prices, and supply/demand."""
    
    def __init__(self, initial_prices: Optional[Dict[str, float]] = None):
        """
        Initialize market with goods.
        
        Args:
            initial_prices: Optional dict of good -> initial price
        """
        self.goods: Dict[str, GoodState] = {}
        
        # Initialize all goods
        for good in GOODS:
            initial_price = 1.0
            if initial_prices and good in initial_prices:
                initial_price = initial_prices[good]
            
            self.goods[good] = GoodState(quantity=0.0, price=initial_price)
        
        # Track supply/demand for this tick
        self._demand: Dict[str, float] = {good: 0.0 for good in GOODS}
        self._supply: Dict[str, float] = {good: 0.0 for good in GOODS}
    
    def get_price(self, good: str) -> float:
        """Get current price of a good."""
        return self.goods.get(good, GoodState()).price
    
    def get_quantity(self, good: str) -> float:
        """Get available quantity of a good."""
        return self.goods.get(good, GoodState()).quantity
    
    def buy(self, good: str, quantity: float, max_price: Optional[float] = None) -> tuple[bool, float]:
        """
        Attempt to buy a good.
        
        Args:
            good: Good to buy
            quantity: Quantity to buy
            max_price: Maximum price willing to pay (optional)
        
        Returns:
            (success, total_cost) tuple
        """
        if good not in self.goods:
            return False, 0.0
        
        good_state = self.goods[good]
        
        # Check if enough quantity available
        if good_state.quantity < quantity:
            return False, 0.0
        
        # Check price if max_price specified
        if max_price is not None and good_state.price > max_price:
            return False, 0.0
        
        # Record demand
        self._demand[good] += quantity
        
        # Execute purchase
        total_cost = good_state.price * quantity
        good_state.quantity -= quantity
        
        return True, total_cost
    
    def sell(self, good: str, quantity: float, min_price: Optional[float] = None) -> tuple[bool, float]:
        """
        Attempt to sell a good.
        
        Args:
            good: Good to sell
            quantity: Quantity to sell
            min_price: Minimum price willing to accept (optional)
        
        Returns:
            (success, total_revenue) tuple
        """
        if good not in self.goods:
            return False, 0.0
        
        good_state = self.goods[good]
        
        # Check price if min_price specified
        if min_price is not None and good_state.price < min_price:
            return False, 0.0
        
        # Record supply
        self._supply[good] += quantity
        
        # Execute sale
        total_revenue = good_state.price * quantity
        good_state.quantity += quantity
        
        return True, total_revenue
    
    def add_supply(self, good: str, quantity: float):
        """Add supply to market (e.g., from production)."""
        if good in self.goods:
            self.goods[good].quantity += quantity
            self._supply[good] += quantity
    
    def update_prices(self):
        """
        Update prices based on supply and demand.
        
        Formula: new_price = old_price * (1 + alpha * (demand - supply) / max(supply, 1))
        """
        for good in GOODS:
            good_state = self.goods[good]
            demand = self._demand[good]
            supply = self._supply[good]
            
            # Update price
            if supply > 0:
                price_change = PRICE_ALPHA * (demand - supply) / supply
            else:
                # If no supply, price increases with demand
                price_change = PRICE_ALPHA * demand if demand > 0 else -PRICE_ALPHA * 0.1
            
            new_price = good_state.price * (1 + price_change)
            
            # Ensure price doesn't go below 0.01
            good_state.price = max(0.01, new_price)
        
        # Reset demand/supply for next tick
        self._demand = {good: 0.0 for good in GOODS}
        self._supply = {good: 0.0 for good in GOODS}
    
    def __repr__(self) -> str:
        goods_str = ", ".join([
            f"{good}: qty={self.goods[good].quantity:.1f}, price={self.goods[good].price:.2f}"
            for good in GOODS
        ])
        return f"Market({goods_str})"

