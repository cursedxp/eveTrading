#!/usr/bin/env python3
"""
Create test data for frontend verification
"""

from datetime import datetime
from mongodb_service import get_mongodb_service

def create_test_routes():
    """Create test route data for frontend"""
    mongo_service = get_mongodb_service()
    
    try:
        # Sample test routes
        test_routes = [
            {
                "item_name": "Tritanium",
                "type_id": 34,
                "buy_system": "Jita",
                "sell_system": "Amarr",
                "buy_price": 5.50,
                "sell_price": 6.20,
                "gross_profit": 0.70,
                "net_profit": 68600,
                "net_profit_percent": 11.8,
                "volume_available": 100000,
                "competition_level": "Medium",
                "risk_level": "Low",
                "confidence_score": 0.9,
                "route_type": "Cross-System",
                "estimated_time": 25,
                "category": "minerals",
                "transport_cost": 1100,
                "profit_margin": 0.118,
                "ai_verdict": "GOOD",
                "ai_reasoning": "good - decent margins, good profit, high volume",
            },
            {
                "item_name": "Pyerite",
                "type_id": 35,
                "buy_system": "Dodixie",
                "sell_system": "Jita",
                "buy_price": 12.80,
                "sell_price": 14.90,
                "gross_profit": 2.10,
                "net_profit": 103950,
                "net_profit_percent": 15.2,
                "volume_available": 50000,
                "competition_level": "Low",
                "risk_level": "Low",
                "confidence_score": 0.85,
                "route_type": "Cross-System",
                "estimated_time": 32,
                "category": "minerals",
                "transport_cost": 6400,
                "profit_margin": 0.152,
                "ai_verdict": "STRONG",
                "ai_reasoning": "strong - good margins, good profit, good volume",
            },
            {
                "item_name": "Mexallon",
                "type_id": 36,
                "buy_system": "Rens",
                "sell_system": "Amarr",
                "buy_price": 89.50,
                "sell_price": 105.20,
                "gross_profit": 15.70,
                "net_profit": 235500,
                "net_profit_percent": 16.8,
                "volume_available": 15000,
                "competition_level": "Medium",
                "risk_level": "Medium",
                "confidence_score": 0.8,
                "route_type": "Cross-System",
                "estimated_time": 48,
                "category": "minerals",
                "transport_cost": 26850,
                "profit_margin": 0.168,
                "ai_verdict": "STRONG",
                "ai_reasoning": "strong - good margins, good profit, decent volume",
            },
            {
                "item_name": "Rifter",
                "type_id": 587,
                "buy_system": "Hek",
                "sell_system": "Jita",
                "buy_price": 177000,
                "sell_price": 195000,
                "gross_profit": 18000,
                "net_profit": 177460,
                "net_profit_percent": 9.5,
                "volume_available": 10,
                "competition_level": "High",
                "risk_level": "Medium",
                "confidence_score": 0.7,
                "route_type": "Cross-System",
                "estimated_time": 52,
                "category": "ships",
                "transport_cost": 3540,
                "profit_margin": 0.095,
                "ai_verdict": "CONSIDER",
                "ai_reasoning": "consider - decent margins, small profit, decent volume",
            },
            {
                "item_name": "Damage Control II",
                "type_id": 2048,
                "buy_system": "Amarr",
                "sell_system": "Jita",
                "buy_price": 2850000,
                "sell_price": 3200000,
                "gross_profit": 350000,
                "net_profit": 343000,
                "net_profit_percent": 11.8,
                "volume_available": 5,
                "competition_level": "Medium",
                "risk_level": "Medium",
                "confidence_score": 0.75,
                "route_type": "Cross-System",
                "estimated_time": 20,
                "category": "modules",
                "transport_cost": 7000,
                "profit_margin": 0.118,
                "ai_verdict": "GOOD",
                "ai_reasoning": "good - good margins, decent profit, decent volume",
            }
        ]
        
        # Create analysis summary
        analysis_data = {
            "timestamp": datetime.utcnow(),
            "total_routes": len(test_routes),
            "profitable_routes": len(test_routes),
            "avg_profit_percent": sum(r["net_profit_percent"] for r in test_routes) / len(test_routes),
            "top_routes": test_routes,  # Store all as top routes
            "routes": test_routes,     # Store all routes
            "system_rankings": {
                "Jita": "A+",
                "Amarr": "A",
                "Dodixie": "B+",
                "Rens": "B",
                "Hek": "B-"
            },
            "recommendations": [
                "Focus on Tritanium and Pyerite for high-volume trades",
                "Consider Mexallon for higher margins",
                "Monitor Rifter prices for quick profits",
                "Damage Control II offers good module trading opportunities"
            ],
            "categories_analyzed": ["minerals", "ships", "modules"],
            "api_calls_made": 5,
            "efficiency_improvement": "64x fewer API calls vs original system"
        }
        
        # Save to route_analysis_v2 collection
        collection = mongo_service.db.route_analysis_v2
        result = collection.insert_one(analysis_data)
        
        print(f"✅ Created test data with {len(test_routes)} sample routes")
        print(f"📄 MongoDB Document ID: {result.inserted_id}")
        
        # Display sample routes
        print("\n🎯 SAMPLE ROUTES CREATED:")
        print(f"{'Item':<18} {'Route':<12} {'Profit':<12} {'Margin':<8} {'AI Verdict'}")
        print("-" * 70)
        
        for route in test_routes:
            route_str = f"{route['buy_system'][:3]}→{route['sell_system'][:3]}"
            print(f"{route['item_name'][:17]:<18} {route_str:<12} "
                  f"{route['net_profit']:>11,.0f} {route['net_profit_percent']:>7.1f}% "
                  f"{route['ai_verdict']}")
        
        print(f"\n🌐 Frontend should now display {len(test_routes)} profitable routes!")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
    finally:
        mongo_service.close()

if __name__ == "__main__":
    create_test_routes()