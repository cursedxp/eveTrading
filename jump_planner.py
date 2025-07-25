#!/usr/bin/env python3
"""
EVE Trading System - Jump Planning and Efficiency Planning
Calculates optimal transport routes based on cargo ship types and jump ranges.
"""

import asyncio
import aiohttp
import json
import math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CargoShip:
    """Cargo ship specifications for transport planning"""
    name: str
    cargo_capacity: int  # m³
    jump_range: float  # light years
    fuel_consumption: float  # fuel per jump
    fuel_cost: float  # ISK per fuel unit
    ship_cost: float  # ISK to purchase
    insurance_cost: float  # ISK per trip
    max_jumps_per_trip: int
    security_restrictions: List[str]  # ['high', 'low', 'null']
    
@dataclass
class JumpRoute:
    """Calculated jump route between systems"""
    origin: str
    destination: str
    ship_type: str
    total_distance: float  # light years
    jumps_required: int
    fuel_cost: float
    insurance_cost: float
    total_cost: float
    cargo_capacity: int
    cost_per_m3: float
    route_path: List[str]
    security_route: List[str]
    estimated_time: int  # minutes
    
@dataclass
class TransportEfficiency:
    """Transport efficiency analysis"""
    item_name: str
    quantity: int
    volume_per_unit: float
    total_volume: float
    buy_price: float
    sell_price: float
    gross_profit: float
    transport_cost: float
    net_profit: float
    profit_margin: float
    recommended_ship: str
    alternative_routes: List[JumpRoute]

class JumpPlanner:
    """Jump planning and efficiency analysis for EVE trading"""
    
    def __init__(self):
        # EVE cargo ship specifications
        self.cargo_ships = {
            'mammoth': CargoShip(
                name='Mammoth',
                cargo_capacity=620000,  # m³
                jump_range=5.0,  # light years
                fuel_consumption=1000,
                fuel_cost=5000,  # ISK per fuel unit
                ship_cost=50000000,  # 50M ISK
                insurance_cost=1000000,  # 1M ISK per trip
                max_jumps_per_trip=10,
                security_restrictions=['high', 'low']
            ),
            'fenrir': CargoShip(
                name='Fenrir',
                cargo_capacity=1200000,  # m³
                jump_range=6.0,
                fuel_consumption=1500,
                fuel_cost=5000,
                ship_cost=80000000,  # 80M ISK
                insurance_cost=1500000,  # 1.5M ISK per trip
                max_jumps_per_trip=15,
                security_restrictions=['high', 'low']
            ),
            'providence': CargoShip(
                name='Providence',
                cargo_capacity=110000,  # m³
                jump_range=4.0,
                fuel_consumption=800,
                fuel_cost=5000,
                ship_cost=20000000,  # 20M ISK
                insurance_cost=500000,  # 500K ISK per trip
                max_jumps_per_trip=8,
                security_restrictions=['high', 'low']
            ),
            'occator': CargoShip(
                name='Occator',
                cargo_capacity=320000,  # m³
                jump_range=5.5,
                fuel_consumption=1200,
                fuel_cost=5000,
                ship_cost=35000000,  # 35M ISK
                insurance_cost=800000,  # 800K ISK per trip
                max_jumps_per_trip=12,
                security_restrictions=['high', 'low']
            ),
            'ark': CargoShip(
                name='Ark',
                cargo_capacity=130000,  # m³
                jump_range=4.5,
                fuel_consumption=900,
                fuel_cost=5000,
                ship_cost=25000000,  # 25M ISK
                insurance_cost=600000,  # 600K ISK per trip
                max_jumps_per_trip=10,
                security_restrictions=['high', 'low']
            )
        }
        
        # EVE system distances (simplified - in practice would use ESI API)
        self.system_distances = {
            ('Jita', 'Amarr'): 15.2,
            ('Jita', 'Dodixie'): 12.8,
            ('Jita', 'Rens'): 18.5,
            ('Jita', 'Hek'): 22.1,
            ('Amarr', 'Dodixie'): 8.3,
            ('Amarr', 'Rens'): 25.7,
            ('Amarr', 'Hek'): 19.4,
            ('Dodixie', 'Rens'): 9.2,
            ('Dodixie', 'Hek'): 11.6,
            ('Rens', 'Hek'): 6.8,
            # Add more system pairs as needed
        }
        
        # System security classifications
        self.system_security = {
            'Jita': 'high',
            'Amarr': 'high', 
            'Dodixie': 'high',
            'Rens': 'high',
            'Hek': 'high',
            'Perimeter': 'high',
            'New Caldari': 'high',
            'Old Man Star': 'low',
            'Oursulaert': 'high',
            'Niarja': 'high'
        }
        
        # Item volume data (m³ per unit)
        self.item_volumes = {
            'Tritanium': 0.01,
            'Mexallon': 0.01,
            'Pyerite': 0.01,
            'Isogen': 0.01,
            'Nocxium': 0.01,
            'Zydrine': 0.01,
            'Megacyte': 0.01,
            'Warrior II': 0.01,
            'Construction Blocks': 0.1,
            'Mechanical Parts': 0.1,
            'Antimatter Charge S': 0.001,
            'Merlin': 10000,  # 10,000 m³
            'Raven': 50000,    # 50,000 m³
            'Megathron': 45000, # 45,000 m³
            'Dominix': 50000,   # 50,000 m³
        }
    
    def get_distance(self, system1: str, system2: str) -> float:
        """Get distance between two systems"""
        # Check both directions
        direct = (system1, system2)
        reverse = (system2, system1)
        
        if direct in self.system_distances:
            return self.system_distances[direct]
        elif reverse in self.system_distances:
            return self.system_distances[reverse]
        else:
            # Estimate distance based on system names
            # In practice, this would use ESI API for accurate distances
            return 20.0  # Default estimate
    
    def calculate_jumps(self, distance: float, ship: CargoShip) -> int:
        """Calculate number of jumps required"""
        return math.ceil(distance / ship.jump_range)
    
    def calculate_fuel_cost(self, jumps: int, ship: CargoShip) -> float:
        """Calculate total fuel cost for journey"""
        return jumps * ship.fuel_consumption * ship.fuel_cost
    
    def calculate_route_cost(self, origin: str, destination: str, ship: CargoShip) -> JumpRoute:
        """Calculate complete route cost and details"""
        distance = self.get_distance(origin, destination)
        jumps = self.calculate_jumps(distance, ship)
        fuel_cost = self.calculate_fuel_cost(jumps, ship)
        insurance_cost = ship.insurance_cost
        
        # Estimate route path (simplified)
        route_path = [origin, destination]
        security_route = [self.system_security.get(origin, 'high'), 
                         self.system_security.get(destination, 'high')]
        
        # Estimate travel time (5 minutes per jump)
        estimated_time = jumps * 5
        
        total_cost = fuel_cost + insurance_cost
        cost_per_m3 = total_cost / ship.cargo_capacity if ship.cargo_capacity > 0 else 0
        
        return JumpRoute(
            origin=origin,
            destination=destination,
            ship_type=ship.name,
            total_distance=distance,
            jumps_required=jumps,
            fuel_cost=fuel_cost,
            insurance_cost=insurance_cost,
            total_cost=total_cost,
            cargo_capacity=ship.cargo_capacity,
            cost_per_m3=cost_per_m3,
            route_path=route_path,
            security_route=security_route,
            estimated_time=estimated_time
        )
    
    def find_optimal_ship(self, origin: str, destination: str, cargo_volume: float) -> CargoShip:
        """Find the most cost-effective ship for the cargo volume"""
        best_ship = None
        best_cost_per_m3 = float('inf')
        
        for ship_name, ship in self.cargo_ships.items():
            if cargo_volume <= ship.cargo_capacity:
                route = self.calculate_route_cost(origin, destination, ship)
                if route.cost_per_m3 < best_cost_per_m3:
                    best_cost_per_m3 = route.cost_per_m3
                    best_ship = ship
        
        return best_ship
    
    def analyze_transport_efficiency(self, item_name: str, quantity: int, 
                                   buy_price: float, sell_price: float,
                                   origin: str, destination: str) -> TransportEfficiency:
        """Analyze transport efficiency for a specific trade"""
        
        # Get item volume
        volume_per_unit = self.item_volumes.get(item_name, 0.01)  # Default 0.01 m³
        total_volume = quantity * volume_per_unit
        gross_profit = (sell_price - buy_price) * quantity
        
        # Find optimal ship
        optimal_ship = self.find_optimal_ship(origin, destination, total_volume)
        
        if optimal_ship:
            route = self.calculate_route_cost(origin, destination, optimal_ship)
            transport_cost = route.total_cost
        else:
            transport_cost = 0
            route = None
        
        net_profit = gross_profit - transport_cost
        profit_margin = (net_profit / (buy_price * quantity)) * 100 if buy_price * quantity > 0 else 0
        
        # Find alternative routes with different ships
        alternative_routes = []
        for ship_name, ship in self.cargo_ships.items():
            if ship != optimal_ship and total_volume <= ship.cargo_capacity:
                alt_route = self.calculate_route_cost(origin, destination, ship)
                alternative_routes.append(alt_route)
        
        return TransportEfficiency(
            item_name=item_name,
            quantity=quantity,
            volume_per_unit=volume_per_unit,
            total_volume=total_volume,
            buy_price=buy_price,
            sell_price=sell_price,
            gross_profit=gross_profit,
            transport_cost=transport_cost,
            net_profit=net_profit,
            profit_margin=profit_margin,
            recommended_ship=optimal_ship.name if optimal_ship else "No suitable ship",
            alternative_routes=alternative_routes
        )
    
    def get_ship_comparison(self, origin: str, destination: str, cargo_volume: float) -> List[JumpRoute]:
        """Compare all available ships for a route"""
        routes = []
        
        for ship_name, ship in self.cargo_ships.items():
            if cargo_volume <= ship.cargo_capacity:
                route = self.calculate_route_cost(origin, destination, ship)
                routes.append(route)
        
        # Sort by cost per m³
        routes.sort(key=lambda x: x.cost_per_m3)
        return routes
    
    def display_route_analysis(self, origin: str, destination: str, cargo_volume: float):
        """Display detailed route analysis"""
        print(f"\n🚀 JUMP PLANNING ANALYSIS")
        print(f"==========================================")
        print(f"Origin: {origin}")
        print(f"Destination: {destination}")
        print(f"Cargo Volume: {cargo_volume:,.0f} m³")
        print(f"Distance: {self.get_distance(origin, destination):.1f} light years")
        
        routes = self.get_ship_comparison(origin, destination, cargo_volume)
        
        if not routes:
            print(f"❌ No suitable ships found for {cargo_volume:,.0f} m³ cargo")
            return
        
        print(f"\n📊 SHIP COMPARISON:")
        print(f"{'Ship':<12} {'Jumps':<6} {'Fuel Cost':<12} {'Insurance':<12} {'Total Cost':<12} {'Cost/m³':<10}")
        print(f"{'':-<70}")
        
        for route in routes:
            print(f"{route.ship_type:<12} {route.jumps_required:<6} "
                  f"{route.fuel_cost:>10,.0f} {route.insurance_cost:>10,.0f} "
                  f"{route.total_cost:>10,.0f} {route.cost_per_m3:>8.2f}")
        
        # Show optimal choice
        optimal = routes[0]
        print(f"\n🏆 OPTIMAL CHOICE: {optimal.ship_type}")
        print(f"   Total Cost: {optimal.total_cost:,.0f} ISK")
        print(f"   Cost per m³: {optimal.cost_per_m3:.2f} ISK")
        print(f"   Travel Time: {optimal.estimated_time} minutes")
        print(f"   Security Route: {' → '.join(optimal.security_route)}")
    
    def display_transport_efficiency(self, efficiency: TransportEfficiency):
        """Display transport efficiency analysis"""
        print(f"\n📦 TRANSPORT EFFICIENCY ANALYSIS")
        print(f"==========================================")
        print(f"Item: {efficiency.item_name}")
        print(f"Quantity: {efficiency.quantity:,}")
        print(f"Volume: {efficiency.total_volume:,.0f} m³")
        print(f"Buy Price: {efficiency.buy_price:,.2f} ISK")
        print(f"Sell Price: {efficiency.sell_price:,.2f} ISK")
        print(f"Gross Profit: {efficiency.gross_profit:,.0f} ISK")
        print(f"Transport Cost: {efficiency.transport_cost:,.0f} ISK")
        print(f"Net Profit: {efficiency.net_profit:,.0f} ISK")
        print(f"Profit Margin: {efficiency.profit_margin:.1f}%")
        print(f"Recommended Ship: {efficiency.recommended_ship}")
        
        if efficiency.alternative_routes:
            print(f"\n🔄 ALTERNATIVE ROUTES:")
            for route in efficiency.alternative_routes[:3]:  # Show top 3
                print(f"   {route.ship_type}: {route.total_cost:,.0f} ISK "
                      f"({route.cost_per_m3:.2f} ISK/m³)")

async def main():
    """Main function to demonstrate jump planning"""
    planner = JumpPlanner()
    
    print("🚀 EVE Trading System - Jump Planning & Efficiency")
    print("=" * 60)
    
    # Example 1: Route analysis
    print("\n1️⃣ ROUTE ANALYSIS EXAMPLE")
    planner.display_route_analysis("Jita", "Amarr", 500000)  # 500k m³ cargo
    
    # Example 2: Transport efficiency
    print("\n2️⃣ TRANSPORT EFFICIENCY EXAMPLE")
    efficiency = planner.analyze_transport_efficiency(
        item_name="Warrior II",
        quantity=1000,
        buy_price=4050,
        sell_price=5000,
        origin="Jita",
        destination="Amarr"
    )
    planner.display_transport_efficiency(efficiency)
    
    # Example 3: Large cargo transport
    print("\n3️⃣ LARGE CARGO TRANSPORT EXAMPLE")
    efficiency2 = planner.analyze_transport_efficiency(
        item_name="Mechanical Parts",
        quantity=100,
        buy_price=11390000,
        sell_price=14150000,
        origin="Jita",
        destination="Rens"
    )
    planner.display_transport_efficiency(efficiency2)
    
    # Example 4: Ship comparison for different routes
    print("\n4️⃣ SHIP COMPARISON FOR DIFFERENT ROUTES")
    routes = [
        ("Jita", "Dodixie", 200000),
        ("Amarr", "Hek", 800000),
        ("Dodixie", "Rens", 300000)
    ]
    
    for origin, dest, volume in routes:
        print(f"\n📍 {origin} → {dest} ({volume:,} m³)")
        planner.display_route_analysis(origin, dest, volume)

if __name__ == "__main__":
    asyncio.run(main()) 