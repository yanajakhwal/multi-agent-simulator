import random
from dataclasses import dataclass, field
from typing import Dict, List


PRICE_ALPHA = 0.1 # sensitivity of price to supply/demand
NUM_CONSUMERS = 10
NUM_PRODUCERS = 3
INITIAL_CONSUMER_WEALTH = 50.0
INITIAL_FOOD_QUANTITY = 20.0
INITIAL_FOOD_PRICE = 3.0
class Agent:
    id: str
    role: str # either "consumer" or "producer" 
    wealth: float
    health: 10.0 
    inventory: Dict[str, float]

    def isAlive(self) -> bool:
        return self.health > 0


@dataclass
class Market:
    goods: Dict[str, Dict[float, int]] # {"good": {"price": price, "quantity": quantity}}

    def getPrice(self, good: str) -> float:
        return self.goods[good]["price"]

    def getQuantity(self, good: str) -> float:
        return self.goods[good]["quantity"]

    def addSupply(self, good: str, newGoods: int) -> None:
        self.goods[good]["quantity"] += newGoods
    
    def removeSupply(self, good: str, usedSupply: int) -> None:
        available = self.goods[good]["quantity"]
        self.goods[good]["quantity"] = max(available - usedSupply, 0)
     
    def updatePrice(self, good: str, supply: float, demand: float) -> None:
        oldPrice = self.goods[good]["price"]
        if supply <= 0 and demand <= 0:
            return
        imbalance = (demand - supply) / max(supply, 1.0)
        newPrice = max(0.1, oldPrice * (1.0 + PRICE_ALPHA * imbalance))
        self.goods[good]["price"] = newPrice


@dataclass
class World:
    agents: List[Agent]
    market: Market


def createInitialWorld() -> World:
    agents: List[World] = []

    # consumers 
    for i in range(NUM_CONSUMERS):
        agents.append(
            Agent(
                id = f"C{i}",
                role = "consumer",
                wealth = INITIAL_CONSUMER_WEALTH
            )
        )

    # producers 
    for i in range(NUM_PRODUCERS):
        agents.append(
            Agent(
                id = f"P{i}",
                role = "producer",
                wealth = NUM_PRODUCERS
            )
        )
    
    market = Market(
        goods = {
            "food": {
                "quantity": INITIAL_FOOD_QUANTITY,
                "price":INITIAL_FOOD_PRICE
            }
        }
    )
    
    return World(agents=agents, market=market)

def main():
    pass