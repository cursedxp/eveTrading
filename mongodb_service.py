"""
MongoDB Service for EVE Trading System
Handles storing and retrieving market analysis data from MongoDB
"""

import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "eve_trading"):
        """Initialize MongoDB connection"""
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        
        # Collections
        self.market_analysis = self.db.market_analysis
        self.discovered_items = self.db.discovered_items
        self.market_orders = self.db.market_orders
        self.trading_signals = self.db.trading_signals
        
        # Create indexes for better performance
        self._create_indexes()
        
    def _create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Market analysis indexes
            self.market_analysis.create_index([("system_name", 1), ("analysis_timestamp", -1)])
            self.market_analysis.create_index([("analysis_timestamp", -1)])
            
            # Discovered items indexes
            self.discovered_items.create_index([("type_id", 1)])
            self.discovered_items.create_index([("name", 1)])
            self.discovered_items.create_index([("overall_score", -1)])
            
            # Market orders indexes
            self.market_orders.create_index([("type_id", 1), ("order_type", 1)])
            self.market_orders.create_index([("location_id", 1)])
            
            # Trading signals indexes
            self.trading_signals.create_index([("system_name", 1), ("timestamp", -1)])
            self.trading_signals.create_index([("item_name", 1)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def store_market_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Store market analysis data in MongoDB"""
        try:
            # Add timestamp if not present
            if "analysis_timestamp" not in analysis_data:
                analysis_data["analysis_timestamp"] = datetime.utcnow()
            
            # Ensure proper data types
            if isinstance(analysis_data.get("analysis_timestamp"), str):
                analysis_data["analysis_timestamp"] = datetime.fromisoformat(
                    analysis_data["analysis_timestamp"].replace('Z', '+00:00')
                )
            
            # Insert the document
            result = self.market_analysis.insert_one(analysis_data)
            logger.info(f"Market analysis stored with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing market analysis: {e}")
            raise
    
    def get_latest_market_analysis(self, system_name: Optional[str] = None, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Get the most recent market analysis"""
        try:
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Build query
            query = {"analysis_timestamp": {"$gte": cutoff_time}}
            if system_name:
                query["system_name"] = system_name
            
            # Find the most recent analysis
            result = self.market_analysis.find(query).sort("analysis_timestamp", -1).limit(1)
            
            analysis = next(result, None)
            if analysis:
                # Convert ObjectId to string for JSON compatibility
                analysis["_id"] = str(analysis["_id"])
                logger.info(f"Retrieved market analysis for {system_name or 'any system'}")
                return analysis
            else:
                logger.info(f"No recent market analysis found for {system_name or 'any system'}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving market analysis: {e}")
            return None
    
    def store_discovered_items(self, items: List[Dict[str, Any]]) -> int:
        """Store discovered items in MongoDB"""
        try:
            if not items:
                return 0
            
            # Add discovery timestamp to each item
            for item in items:
                if "discovered_at" not in item:
                    item["discovered_at"] = datetime.utcnow()
                elif isinstance(item["discovered_at"], str):
                    item["discovered_at"] = datetime.fromisoformat(
                        item["discovered_at"].replace('Z', '+00:00')
                    )
            
            # Use upsert to avoid duplicates based on type_id
            operations = []
            for item in items:
                operations.append(
                    pymongo.UpdateOne(
                        {"type_id": item["type_id"]},
                        {"$set": item},
                        upsert=True
                    )
                )
            
            result = self.discovered_items.bulk_write(operations)
            logger.info(f"Stored {result.upserted_count} new items, updated {result.modified_count} existing items")
            return result.upserted_count + result.modified_count
            
        except Exception as e:
            logger.error(f"Error storing discovered items: {e}")
            raise
    
    def get_discovered_items(self, limit: int = 100, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """Get discovered items from MongoDB"""
        try:
            query = {"overall_score": {"$gte": min_score}}
            cursor = self.discovered_items.find(query).sort("overall_score", -1).limit(limit)
            
            items = []
            for item in cursor:
                item["_id"] = str(item["_id"])  # Convert ObjectId to string
                items.append(item)
            
            logger.info(f"Retrieved {len(items)} discovered items")
            return items
            
        except Exception as e:
            logger.error(f"Error retrieving discovered items: {e}")
            return []
    
    def store_trading_signals(self, signals: List[Dict[str, Any]], system_name: str) -> int:
        """Store trading signals in MongoDB"""
        try:
            if not signals:
                return 0
            
            # Add metadata to each signal
            for signal in signals:
                signal["system_name"] = system_name
                signal["stored_at"] = datetime.utcnow()
                if "timestamp" not in signal:
                    signal["timestamp"] = datetime.utcnow()
                elif isinstance(signal["timestamp"], str):
                    signal["timestamp"] = datetime.fromisoformat(
                        signal["timestamp"].replace('Z', '+00:00')
                    )
            
            # Insert all signals
            result = self.trading_signals.insert_many(signals)
            logger.info(f"Stored {len(result.inserted_ids)} trading signals for {system_name}")
            return len(result.inserted_ids)
            
        except Exception as e:
            logger.error(f"Error storing trading signals: {e}")
            raise
    
    def get_trading_signals(self, system_name: str, max_age_hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trading signals from MongoDB"""
        try:
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            query = {
                "system_name": system_name,
                "timestamp": {"$gte": cutoff_time}
            }
            
            cursor = self.trading_signals.find(query).sort("timestamp", -1).limit(limit)
            
            signals = []
            for signal in cursor:
                signal["_id"] = str(signal["_id"])  # Convert ObjectId to string
                signals.append(signal)
            
            logger.info(f"Retrieved {len(signals)} trading signals for {system_name}")
            return signals
            
        except Exception as e:
            logger.error(f"Error retrieving trading signals: {e}")
            return []
    
    def cleanup_old_data(self, max_age_days: int = 7):
        """Clean up old data from MongoDB"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
            
            # Clean up old market analysis
            result1 = self.market_analysis.delete_many({"analysis_timestamp": {"$lt": cutoff_time}})
            
            # Clean up old trading signals
            result2 = self.trading_signals.delete_many({"timestamp": {"$lt": cutoff_time}})
            
            logger.info(f"Cleaned up {result1.deleted_count} old market analyses and {result2.deleted_count} old trading signals")
            return result1.deleted_count + result2.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {
                "market_analyses": self.market_analysis.count_documents({}),
                "discovered_items": self.discovered_items.count_documents({}),
                "market_orders": self.market_orders.count_documents({}),
                "trading_signals": self.trading_signals.count_documents({}),
                "database_size": self.db.command("dbStats")["dataSize"],
                "last_updated": datetime.utcnow()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

# Convenience function to get a MongoDB service instance
def get_mongodb_service() -> MongoDBService:
    """Get a MongoDB service instance"""
    return MongoDBService()

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test the MongoDB service
    mongo_service = get_mongodb_service()
    
    try:
        # Test connection and get stats
        stats = mongo_service.get_database_stats()
        print(f"📊 Database Stats: {stats}")
        
        # Test storing and retrieving market analysis
        test_analysis = {
            "system_name": "Test System",
            "total_opportunities": 10,
            "avg_profit_margin": 0.15,
            "market_health": "Good",
            "opportunities": [
                {
                    "item_name": "Test Item",
                    "profit_margin": 0.20,
                    "buy_price": 100,
                    "sell_price": 120
                }
            ]
        }
        
        # Store test data
        analysis_id = mongo_service.store_market_analysis(test_analysis)
        print(f"✅ Stored test analysis with ID: {analysis_id}")
        
        # Retrieve test data
        retrieved = mongo_service.get_latest_market_analysis("Test System")
        if retrieved:
            print(f"✅ Retrieved analysis: {retrieved['system_name']} with {retrieved['total_opportunities']} opportunities")
        
        print("🎉 MongoDB service is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing MongoDB service: {e}")
    finally:
        mongo_service.close()