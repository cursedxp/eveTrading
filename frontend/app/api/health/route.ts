import { NextRequest, NextResponse } from "next/server";
import { MongoClient } from "mongodb";

// MongoDB connection string
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017/";
const DATABASE_NAME = "eve_trading";

async function checkMongoDBHealth() {
  const client = new MongoClient(MONGODB_URI);
  try {
    await client.connect();
    const db = client.db(DATABASE_NAME);
    
    // Test database connection by checking collections
    const collections = await db.listCollections().toArray();
    const collectionNames = collections.map(c => c.name);
    
    // Check if we have data in key collections
    const itemsCount = await db.collection("discovered_items").countDocuments({});
    const routesCount = await db.collection("route_analysis_v2").countDocuments({});
    
    return {
      status: "healthy",
      database: "connected",
      collections: collectionNames,
      data_status: {
        discovered_items: itemsCount,
        route_analysis: routesCount,
      }
    };
  } catch (error) {
    return {
      status: "unhealthy",
      database: "disconnected",
      error: error instanceof Error ? error.message : "Unknown error"
    };
  } finally {
    await client.close();
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log("🏥 Running health check...");
    
    const mongoHealth = await checkMongoDBHealth();
    
    const healthData = {
      success: true,
      status: mongoHealth.status === "healthy" ? "online" : "degraded",
      timestamp: new Date().toISOString(),
      version: "2.0.0",
      system: "EVE Trading System",
      database: mongoHealth,
      services: {
        api: "online",
        mongodb: mongoHealth.status === "healthy" ? "connected" : "disconnected",
        frontend: "online"
      }
    };

    return NextResponse.json(healthData, {
      status: mongoHealth.status === "healthy" ? 200 : 503,
      headers: {
        "Cache-Control": "public, s-maxage=30, stale-while-revalidate=60",
      },
    });
  } catch (error) {
    console.error("Health check API error:", error);

    return NextResponse.json(
      {
        success: false,
        status: "offline",
        error: "Health check failed",
        message: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}
