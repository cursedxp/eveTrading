import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { MongoClient } from "mongodb";

// MongoDB connection string
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017/";
const DATABASE_NAME = "eve_trading";

async function getLatestRouteAnalysis() {
  const client = new MongoClient(MONGODB_URI);
  try {
    await client.connect();
    const db = client.db(DATABASE_NAME);
    
    // Try the new V2 collection first (our MongoDB-based system)
    let collection = db.collection("route_analysis_v2");
    
    // Get the most recent route analysis (within last 2 hours)
    const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000);
    
    let analysis = await collection.findOne(
      { timestamp: { $gte: twoHoursAgo } },
      { sort: { timestamp: -1 } }
    );
    
    // If no recent analysis in V2, get the latest available from V2
    if (!analysis) {
      analysis = await collection.findOne(
        {},
        { sort: { timestamp: -1 } }
      );
    }
    
    // If still no data in V2, fallback to old collection
    if (!analysis) {
      collection = db.collection("route_analysis");
      analysis = await collection.findOne(
        {},
        { sort: { analysis_timestamp: -1 } }
      );
    }
    
    return analysis;
  } finally {
    await client.close();
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log("🔍 Fetching profitable routes analysis...");

    // Get query parameters for pagination and filtering
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50'); // Default to 50 routes
    const category = searchParams.get('category');
    const offset = (page - 1) * limit;

    console.log(`📄 Pagination: page=${page}, limit=${limit}, offset=${offset}`);
    if (category) console.log(`🔍 Category filter: ${category}`);

    // First, try to get recent data from MongoDB
    let routeData = await getLatestRouteAnalysis();
    
    if (!routeData) {
      console.log("🔄 No recent route analysis found, running fresh analysis...");
      // Run the NEW MongoDB-based profitable route finder Python script
      const parentDir = path.join(process.cwd(), "..");
      
      await new Promise<void>((resolve, reject) => {
        const pythonProcess = spawn("python", ["profitable_route_finder_final.py"], {
          cwd: parentDir,
        });

        let outputData = "";
        let errorData = "";

        pythonProcess.stdout.on("data", (data) => {
          outputData += data.toString();
        });

        pythonProcess.stderr.on("data", (data) => {
          errorData += data.toString();
        });

        pythonProcess.on("close", (code) => {
          if (code !== 0) {
            console.error("Python script error:", errorData);
            reject(new Error(errorData || "Python script failed"));
          } else {
            resolve();
          }
        });
      });
      
      // After running the script, try to get the data from MongoDB again
      routeData = await getLatestRouteAnalysis();
    }

    if (!routeData) {
      throw new Error("No route analysis data available");
    }

    console.log("✅ Using route analysis data");

    // Transform the data to match expected format
    // Handle both old and new data formats
    let allRoutes = (routeData.top_routes || routeData.routes || []).map((route: any) => {
      // Parse route string "Amarr→Jita" to extract buy_system and sell_system
      let buy_system = route.buy_system;
      let sell_system = route.sell_system;
      
      if (!buy_system && !sell_system && route.route) {
        const routeParts = route.route.split('→');
        if (routeParts.length === 2) {
          buy_system = routeParts[0].trim();
          sell_system = routeParts[1].trim();
        }
      }
      
      return {
        item_name: route.item_name,
        type_id: route.type_id,
        buy_system: buy_system,
        sell_system: sell_system,
        buy_price: route.buy_price,
        sell_price: route.sell_price,
        gross_profit: route.gross_profit || (route.sell_price - route.buy_price),
        profit_margin: route.profit_margin || ((route.sell_price - route.buy_price) / route.buy_price),
        transport_cost: route.transport_cost || 0,
        net_profit: route.net_profit || (route.sell_price - route.buy_price),
        net_profit_percent: route.net_profit_percent,
        volume_available: route.volume_available,
        competition_level: route.competition_level || 'Unknown',
        risk_level: route.risk_level,
        confidence_score: route.confidence_score,
        route_type: route.route_type || 'Cross-System',
        estimated_time: route.estimated_time || 30,
        action_plan: route.action_plan || `Buy ${route.item_name} in ${buy_system}, sell in ${sell_system}`,
        category: route.category, // New field from V2
      };
    });

    // Apply category filter if specified
    if (category && category !== 'all') {
      allRoutes = allRoutes.filter((route: any) => 
        route.category && route.category.toLowerCase() === category.toLowerCase()
      );
      console.log(`🔍 Filtered to ${allRoutes.length} routes in category: ${category}`);
    }

    // Apply pagination
    const totalRoutes = allRoutes.length;
    const paginatedRoutes = allRoutes.slice(offset, offset + limit);
    const totalPages = Math.ceil(totalRoutes / limit);

    console.log(`📊 Returning ${paginatedRoutes.length} routes (page ${page} of ${totalPages})`);

    const routes = paginatedRoutes;

    return NextResponse.json({
      routes,
      pagination: {
        page: page,
        limit: limit,
        total_routes: totalRoutes,
        total_pages: totalPages,
        has_next: page < totalPages,
        has_prev: page > 1
      },
      summary: {
        total_routes: routeData.total_routes || totalRoutes,
        profitable_routes: routeData.profitable_routes || totalRoutes,
        avg_profit_percent: routeData.avg_profit_percent || 0,
        system_rankings: routeData.system_rankings || {},
        recommendations: routeData.recommendations || [],
        categories_analyzed: routeData.categories_analyzed || [],
      },
      analysis_timestamp: routeData.timestamp || routeData.analysis_timestamp || new Date().toISOString(),
    }, {
      status: 200,
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
      },
    });
  } catch (error) {
    console.error("Profitable routes API error:", error);

    return NextResponse.json(
      {
        error: "Failed to get profitable routes",
        message: error instanceof Error ? error.message : "Unknown error",
        routes: [],
        summary: {
          total_routes: 0,
          profitable_routes: 0,
          avg_profit_percent: 0,
          system_rankings: {},
          recommendations: [],
        },
      },
      { status: 500 }
    );
  }
}
