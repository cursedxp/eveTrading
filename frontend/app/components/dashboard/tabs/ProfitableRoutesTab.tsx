"use client";

import React, { useState, useEffect } from "react";
import { RefreshCw, ArrowRight, Package, TrendingUp, AlertTriangle, ChevronLeft, ChevronRight, Filter } from "lucide-react";
import { OverlayPreloader } from "../../Preloader";

interface ProfitableRoute {
  item_name: string;
  type_id: number;
  buy_system: string;
  sell_system: string;
  buy_price: number;
  sell_price: number;
  gross_profit: number;
  profit_margin: number;
  transport_cost: number;
  net_profit: number;
  net_profit_percent: number;
  volume_available: number;
  competition_level: string;
  risk_level: string;
  confidence_score: number;
  route_type: string;
  estimated_time: number;
  action_plan: string;
  category: string; // New field for category
}

interface PaginationInfo {
  page: number;
  limit: number;
  total_routes: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface RouteAnalysis {
  routes: ProfitableRoute[];
  pagination: PaginationInfo;
  summary: {
    total_routes: number;
    profitable_routes: number;
    avg_profit_percent: number;
    system_rankings: Record<string, number>;
    recommendations: string[];
    categories_analyzed: string[];
  };
  analysis_timestamp: string;
}

interface ProfitableRoutesTabProps {
  onRefresh: () => void;
  loading?: boolean;
}

export const ProfitableRoutesTab: React.FC<ProfitableRoutesTabProps> = ({
  onRefresh,
  loading = false,
}) => {
  const [routeAnalysis, setRouteAnalysis] = useState<RouteAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [pageSize, setPageSize] = useState(25);

  const fetchRouteAnalysis = async (page: number = 1, category: string = 'all', limit: number = 25) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });
      
      if (category !== 'all') {
        params.append('category', category);
      }
      
      const response = await fetch(`/api/profitable-routes?${params}`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `API error: ${response.status}`);
      }
      
      setRouteAnalysis(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch route analysis');
      console.error('Route analysis fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRouteAnalysis(currentPage, selectedCategory, pageSize);
  }, [currentPage, selectedCategory, pageSize]);

  const handleRefresh = () => {
    onRefresh();
    setCurrentPage(1);
    fetchRouteAnalysis(1, selectedCategory, pageSize);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setCurrentPage(1);
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setCurrentPage(1);
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-eve-success';
      case 'medium': return 'text-eve-warning';
      case 'high': return 'text-eve-danger';
      default: return 'text-eve-light';
    }
  };

  const getRouteTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'export': return 'text-blue-400';
      case 'import': return 'text-green-400';
      case 'arbitrage': return 'text-purple-400';
      default: return 'text-eve-light';
    }
  };

  const formatISK = (amount: number) => {
    if (amount >= 1000000000) {
      return `${(amount / 1000000000).toFixed(1)}B`;
    } else if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  if (isLoading && !routeAnalysis) {
    return (
      <div className="eve-card">
        <OverlayPreloader isLoading={true} message="🚀 Analyzing profitable routes across EVE systems..." />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="eve-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold flex items-center space-x-2">
              <Package className="h-5 w-5 text-eve-highlight" />
              <span>Profitable Routes</span>
            </h2>
            <p className="text-sm text-eve-light/70">
              Cross-system trading opportunities with highest profit potential
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {lastUpdate && (
              <span className="text-xs text-eve-light/70">
                Last updated: {lastUpdate}
              </span>
            )}
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="eve-button bg-eve-highlight hover:bg-eve-highlight/80 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        {routeAnalysis && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-eve-accent/10 rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-eve-highlight">
                {routeAnalysis.pagination.total_routes}
              </div>
              <div className="text-xs text-eve-light/70">Total Routes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-eve-success">
                {routeAnalysis.summary.profitable_routes}
              </div>
              <div className="text-xs text-eve-light/70">Profitable</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-eve-warning">
                {routeAnalysis.summary.avg_profit_percent.toFixed(1)}%
              </div>
              <div className="text-xs text-eve-light/70">Avg Profit</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-eve-light">
                {routeAnalysis.summary.categories_analyzed.length}
              </div>
              <div className="text-xs text-eve-light/70">Categories</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-eve-accent">
                {routeAnalysis.pagination.page}/{routeAnalysis.pagination.total_pages}
              </div>
              <div className="text-xs text-eve-light/70">Page</div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="eve-card border-eve-danger/50 bg-eve-danger/10">
          <div className="flex items-center space-x-2 text-eve-danger">
            <AlertTriangle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Filters and Controls */}
      {routeAnalysis && (
        <div className="eve-card">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-eve-highlight" />
                <label className="text-sm font-medium">Category:</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => handleCategoryChange(e.target.value)}
                  className="bg-eve-accent/20 border border-eve-accent/30 rounded px-3 py-1 text-sm focus:outline-none focus:border-eve-highlight"
                >
                  <option value="all">All Categories</option>
                  {routeAnalysis.summary.categories_analyzed.map((category) => (
                    <option key={category} value={category.toLowerCase()}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium">Per Page:</label>
                <select
                  value={pageSize}
                  onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                  className="bg-eve-accent/20 border border-eve-accent/30 rounded px-3 py-1 text-sm focus:outline-none focus:border-eve-highlight"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-eve-light/70">
                Showing {((routeAnalysis.pagination.page - 1) * routeAnalysis.pagination.limit) + 1}-
                {Math.min(routeAnalysis.pagination.page * routeAnalysis.pagination.limit, routeAnalysis.pagination.total_routes)} 
                of {routeAnalysis.pagination.total_routes}
              </span>
              
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => handlePageChange(routeAnalysis.pagination.page - 1)}
                  disabled={!routeAnalysis.pagination.has_prev}
                  className="p-1 rounded border border-eve-accent/30 hover:bg-eve-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                
                <span className="px-3 py-1 text-sm">
                  {routeAnalysis.pagination.page} / {routeAnalysis.pagination.total_pages}
                </span>
                
                <button
                  onClick={() => handlePageChange(routeAnalysis.pagination.page + 1)}
                  disabled={!routeAnalysis.pagination.has_next}
                  className="p-1 rounded border border-eve-accent/30 hover:bg-eve-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Routes Table */}
      {routeAnalysis && routeAnalysis.routes.length > 0 ? (
        <div className="eve-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {selectedCategory === 'all' ? 'All Profitable Routes' : `${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Routes`}
            </h3>
            <span className="text-sm text-eve-light/70">
              {routeAnalysis.routes.length} routes on this page
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="eve-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Item</th>
                  <th>Route</th>
                  <th>Buy Price</th>
                  <th>Sell Price</th>
                  <th>Net Profit</th>
                  <th>Transport</th>
                  <th>Volume Available</th>
                  <th title="Total ISK needed to buy all available volume">Investment</th>
                  <th title="Total ISK profit if all volume is traded">Total Profit</th>
                  <th>Risk</th>
                  <th>Confidence</th>
                  <th>Type</th>
                </tr>
              </thead>
              <tbody>
                {routeAnalysis.routes.map((route, index) => (
                  <tr key={`${route.type_id}-${index}`}>
                    <td>
                      <span className="inline-block px-2 py-1 text-xs rounded-full bg-eve-accent/20 text-eve-highlight">
                        {route.category}
                      </span>
                    </td>
                    <td className="font-medium">{route.item_name}</td>
                    <td>
                      <div className="flex items-center space-x-2">
                        <span className="text-eve-highlight">{route.buy_system}</span>
                        <ArrowRight className="h-3 w-3 text-eve-light/50" />
                        <span className="text-eve-success">{route.sell_system}</span>
                      </div>
                    </td>
                    <td>{formatISK(route.buy_price)} ISK</td>
                    <td>{formatISK(route.sell_price)} ISK</td>
                    <td className="profit-positive font-medium">
                      {route.net_profit_percent.toFixed(1)}%
                    </td>
                    <td>{formatISK(route.transport_cost)} ISK</td>
                    <td>{route.volume_available.toLocaleString()}</td>
                    <td className="font-medium text-eve-warning">
                      {formatISK(route.volume_available * route.buy_price)} ISK
                    </td>
                    <td className="font-medium text-eve-success">
                      {formatISK(route.volume_available * route.net_profit)} ISK
                    </td>
                    <td className={getRiskColor(route.risk_level)}>
                      {route.risk_level}
                    </td>
                    <td>{(route.confidence_score * 100).toFixed(0)}%</td>
                    <td className={getRouteTypeColor(route.route_type)}>
                      {route.route_type}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Bottom Pagination */}
          {routeAnalysis.pagination.total_pages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-eve-accent/30">
              <div className="text-sm text-eve-light/70">
                Showing {((routeAnalysis.pagination.page - 1) * routeAnalysis.pagination.limit) + 1}-
                {Math.min(routeAnalysis.pagination.page * routeAnalysis.pagination.limit, routeAnalysis.pagination.total_routes)} 
                of {routeAnalysis.pagination.total_routes} routes
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handlePageChange(1)}
                  disabled={routeAnalysis.pagination.page === 1}
                  className="px-3 py-1 text-sm rounded border border-eve-accent/30 hover:bg-eve-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  First
                </button>
                
                <button
                  onClick={() => handlePageChange(routeAnalysis.pagination.page - 1)}
                  disabled={!routeAnalysis.pagination.has_prev}
                  className="p-1 rounded border border-eve-accent/30 hover:bg-eve-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                
                <span className="px-3 py-1 text-sm bg-eve-accent/20 rounded">
                  {routeAnalysis.pagination.page} / {routeAnalysis.pagination.total_pages}
                </span>
                
                <button
                  onClick={() => handlePageChange(routeAnalysis.pagination.page + 1)}
                  disabled={!routeAnalysis.pagination.has_next}
                  className="p-1 rounded border border-eve-accent/30 hover:bg-eve-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
                
                <button
                  onClick={() => handlePageChange(routeAnalysis.pagination.total_pages)}
                  disabled={routeAnalysis.pagination.page === routeAnalysis.pagination.total_pages}
                  className="px-3 py-1 text-sm rounded border border-eve-accent/30 hover:bg-eve-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Last
                </button>
              </div>
            </div>
          )}
        </div>
      ) : routeAnalysis && routeAnalysis.routes.length === 0 ? (
        <div className="eve-card">
          <div className="text-center py-8">
            <Package className="h-12 w-12 text-eve-light/30 mx-auto mb-4" />
            <div className="text-lg mb-2 text-eve-light">No Profitable Routes Found</div>
            <div className="text-sm text-eve-light/70 mb-4">
              Current market conditions show no profitable cross-system trading opportunities.
              This indicates efficient market pricing across all analyzed systems.
            </div>
            <div className="text-xs text-eve-light/50">
              💡 Tip: Try refreshing later as market conditions change frequently
            </div>
          </div>
        </div>
      ) : null}

      {/* System Rankings */}
      {routeAnalysis && Object.keys(routeAnalysis.summary.system_rankings).length > 0 && (
        <div className="eve-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-eve-highlight" />
            <span>System Rankings</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(routeAnalysis.summary.system_rankings)
              .slice(0, 6)
              .map(([system, avgProfit], index) => (
                <div
                  key={system}
                  className="p-3 bg-eve-accent/10 rounded-lg border border-eve-accent/30"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{system}</span>
                    <span className="text-sm text-eve-highlight">
                      #{index + 1}
                    </span>
                  </div>
                  <div className="text-sm text-eve-light/70">
                    {avgProfit.toFixed(1)}% avg profit
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {routeAnalysis && routeAnalysis.summary.recommendations.length > 0 && (
        <div className="eve-card">
          <h3 className="text-lg font-semibold mb-4">💡 Recommendations</h3>
          <div className="space-y-2">
            {routeAnalysis.summary.recommendations.map((rec, index) => (
              <div
                key={index}
                className="flex items-start space-x-2 text-sm"
              >
                <span className="text-eve-highlight">•</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};