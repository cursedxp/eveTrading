"""
EVE Items Database - Popular trading items with metadata
Contains type_id, name, category, and trading characteristics
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class EVEItem:
    type_id: int
    name: str
    category: str
    subcategory: str
    avg_volume: int  # Average daily volume
    price_volatility: float  # Price volatility (0-1)
    profit_potential: float  # Profit potential score (0-1)
    market_activity: str  # "High", "Medium", "Low"
    description: str

# Popular EVE Trading Items Database
EVE_ITEMS = {
    # Minerals (High Volume, Low Profit, High Activity)
    34: EVEItem(34, "Tritanium", "Mineral", "Basic Minerals", 1000000, 0.3, 0.2, "High", "Basic construction material"),
    35: EVEItem(35, "Pyerite", "Mineral", "Basic Minerals", 800000, 0.3, 0.2, "High", "Basic construction material"),
    36: EVEItem(36, "Mexallon", "Mineral", "Basic Minerals", 600000, 0.4, 0.3, "High", "Advanced construction material"),
    37: EVEItem(37, "Isogen", "Mineral", "Basic Minerals", 400000, 0.5, 0.4, "High", "Advanced construction material"),
    38: EVEItem(38, "Nocxium", "Mineral", "Basic Minerals", 300000, 0.6, 0.5, "Medium", "Advanced construction material"),
    39: EVEItem(39, "Zydrine", "Mineral", "Basic Minerals", 200000, 0.7, 0.6, "Medium", "Advanced construction material"),
    40: EVEItem(40, "Megacyte", "Mineral", "Basic Minerals", 100000, 0.8, 0.7, "Medium", "Advanced construction material"),
    
    # Ice Products (Medium Volume, Medium Profit)
    16262: EVEItem(16262, "Strontium Clathrates", "Ice Product", "Fuel Blocks", 50000, 0.4, 0.5, "Medium", "Fuel block component"),
    16263: EVEItem(16263, "Heavy Water", "Ice Product", "Fuel Blocks", 40000, 0.4, 0.5, "Medium", "Fuel block component"),
    16264: EVEItem(16264, "Liquid Ozone", "Ice Product", "Fuel Blocks", 30000, 0.5, 0.6, "Medium", "Fuel block component"),
    16265: EVEItem(16265, "Helium Isotopes", "Ice Product", "Fuel Blocks", 20000, 0.6, 0.7, "Medium", "Fuel block component"),
    
    # Planetary Materials (Variable Volume, High Profit)
    44: EVEItem(44, "Enriched Uranium", "Planetary", "Heavy Metals", 10000, 0.7, 0.8, "Medium", "Planetary resource"),
    45: EVEItem(45, "Toxic Metals", "Planetary", "Heavy Metals", 8000, 0.7, 0.8, "Medium", "Planetary resource"),
    46: EVEItem(46, "Reactive Metals", "Planetary", "Heavy Metals", 6000, 0.8, 0.8, "Medium", "Planetary resource"),
    
    # Components (Low Volume, High Profit)
    11529: EVEItem(11529, "Mechanical Parts", "Component", "Ship Components", 5000, 0.8, 0.9, "Low", "Ship construction component"),
    11530: EVEItem(11530, "Construction Blocks", "Component", "Ship Components", 3000, 0.8, 0.9, "Low", "Ship construction component"),
    11531: EVEItem(11531, "Hull Sections", "Component", "Ship Components", 2000, 0.9, 0.9, "Low", "Ship construction component"),
    
    # Ammunition (High Volume, Medium Profit)
    1: EVEItem(1, "Antimatter Charge S", "Ammunition", "Projectile", 50000, 0.4, 0.5, "High", "Small projectile ammunition"),
    2: EVEItem(2, "Antimatter Charge M", "Ammunition", "Projectile", 40000, 0.4, 0.5, "High", "Medium projectile ammunition"),
    3: EVEItem(3, "Antimatter Charge L", "Ammunition", "Projectile", 30000, 0.5, 0.6, "Medium", "Large projectile ammunition"),
    
    # Drones (Medium Volume, High Profit)
    2203: EVEItem(2203, "Warrior II", "Drone", "Combat Drones", 15000, 0.6, 0.7, "Medium", "Combat drone"),
    2205: EVEItem(2205, "Hammerhead II", "Drone", "Combat Drones", 12000, 0.6, 0.7, "Medium", "Combat drone"),
    2207: EVEItem(2207, "Ogre II", "Drone", "Combat Drones", 10000, 0.7, 0.8, "Medium", "Combat drone"),
    
    # Modules (Low Volume, Very High Profit)
    2048: EVEItem(2048, "Adaptive Invulnerability Field I", "Module", "Shield Modules", 1000, 0.9, 0.9, "Low", "Shield module"),
    2049: EVEItem(2049, "Adaptive Invulnerability Field II", "Module", "Shield Modules", 500, 0.9, 0.95, "Low", "Advanced shield module"),
    2050: EVEItem(2050, "Adaptive Invulnerability Field II", "Module", "Shield Modules", 300, 0.95, 0.95, "Low", "Advanced shield module"),
    
    # Ships (Very Low Volume, Very High Profit)
    670: EVEItem(670, "Merlin", "Ship", "Frigate", 100, 0.9, 0.95, "Low", "Combat frigate"),
    671: EVEItem(671, "Punisher", "Ship", "Frigate", 80, 0.9, 0.95, "Low", "Combat frigate"),
    672: EVEItem(672, "Rifter", "Ship", "Frigate", 120, 0.9, 0.95, "Low", "Combat frigate"),
    
    # Tech 2 Materials (Medium Volume, High Profit)
    34: EVEItem(34, "Tritanium", "Mineral", "Basic Minerals", 1000000, 0.3, 0.2, "High", "Basic construction material"),
    35: EVEItem(35, "Pyerite", "Mineral", "Basic Minerals", 800000, 0.3, 0.2, "High", "Basic construction material"),
    36: EVEItem(36, "Mexallon", "Mineral", "Basic Minerals", 600000, 0.4, 0.3, "High", "Advanced construction material"),
    37: EVEItem(37, "Isogen", "Mineral", "Basic Minerals", 400000, 0.5, 0.4, "High", "Advanced construction material"),
    38: EVEItem(38, "Nocxium", "Mineral", "Basic Minerals", 300000, 0.6, 0.5, "Medium", "Advanced construction material"),
    39: EVEItem(39, "Zydrine", "Mineral", "Basic Minerals", 200000, 0.7, 0.6, "Medium", "Advanced construction material"),
    40: EVEItem(40, "Megacyte", "Mineral", "Basic Minerals", 100000, 0.8, 0.7, "Medium", "Advanced construction material"),
}

def get_item_by_id(type_id: int) -> Optional[EVEItem]:
    """Get item by type_id"""
    return EVE_ITEMS.get(type_id)

def get_items_by_category(category: str) -> List[EVEItem]:
    """Get all items in a category"""
    return [item for item in EVE_ITEMS.values() if item.category == category]

def get_high_profit_items(min_profit_potential: float = 0.7) -> List[EVEItem]:
    """Get items with high profit potential"""
    return [item for item in EVE_ITEMS.values() if item.profit_potential >= min_profit_potential]

def get_high_volume_items(min_volume: int = 50000) -> List[EVEItem]:
    """Get items with high trading volume"""
    return [item for item in EVE_ITEMS.values() if item.avg_volume >= min_volume]

def get_volatile_items(min_volatility: float = 0.6) -> List[EVEItem]:
    """Get items with high price volatility"""
    return [item for item in EVE_ITEMS.values() if item.price_volatility >= min_volatility]

def get_all_items() -> List[EVEItem]:
    """Get all items"""
    return list(EVE_ITEMS.values())

def get_item_names() -> Dict[int, str]:
    """Get mapping of type_id to name"""
    return {item.type_id: item.name for item in EVE_ITEMS.values()}

def get_trading_recommendations() -> List[EVEItem]:
    """Get recommended items for trading based on multiple factors"""
    recommendations = []
    
    # High profit + medium volume items
    for item in EVE_ITEMS.values():
        if (item.profit_potential >= 0.6 and 
            item.avg_volume >= 10000 and 
            item.price_volatility >= 0.5):
            recommendations.append(item)
    
    # Sort by profit potential
    recommendations.sort(key=lambda x: x.profit_potential, reverse=True)
    return recommendations

if __name__ == "__main__":
    print("EVE Items Database")
    print("=" * 50)
    
    print("\nHigh Profit Items:")
    for item in get_high_profit_items():
        print(f"- {item.name} (ID: {item.type_id}): {item.profit_potential:.1%} profit potential")
    
    print("\nHigh Volume Items:")
    for item in get_high_volume_items():
        print(f"- {item.name} (ID: {item.type_id}): {item.avg_volume:,} avg volume")
    
    print("\nTrading Recommendations:")
    for item in get_trading_recommendations()[:10]:
        print(f"- {item.name} (ID: {item.type_id}): {item.profit_potential:.1%} profit, {item.avg_volume:,} volume") 