"use client";

import React, { useState, useEffect } from "react";
import { useDataFetcher } from "./components/DataFetcher";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  AlertTriangle,
  Rocket,
  Shield,
  Zap,
  Activity,
  Eye,
  RefreshCw,
  Settings,
  MapPin,
  Target,
  Users,
  Globe,
  ArrowUpDown,
  Package,
  Clock,
  Star,
  Search,
  ChevronDown,
  X,
  Navigation,
} from "lucide-react";

interface MarketData {
  type_id: number;
  item_name: string;
  current_price: number;
  price_change: number;
  volume_24h: number;
  profit_margin: number;
  recommendation: string;
}

interface TradingSignal {
  timestamp: string;
  type_id: number;
  item_name: string;
  action: string;
  confidence: number;
  price: number;
  buy_location?: string;
  sell_location?: string;
  transport_cost?: number;
  net_profit_margin?: number;
  signal_type?: string; // "ARBITRAGE", "IMPORT", "EXPORT", "LOCAL"
  action_plan?: string;
}

interface PortfolioItem {
  type_id: number;
  item_name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

interface LocalMarketOpportunity {
  type_id: number;
  item_name: string;
  current_buy_price: number;
  current_sell_price: number;
  profit_margin: number;
  volume_available: number;
  competition_count: number;
  local_demand: string;
  local_supply: string;
  opportunity_type: string;
  score: number;
  recommendation: string;
  action_plan: string;
  sell_location?: string; // New field for specific sell location
  transport_cost?: number; // New field for transport costs
  net_profit_margin?: number; // New field for profit after transport
}

interface SystemAnalysis {
  system_name: string;
  total_opportunities: number;
  avg_profit_margin: number;
  market_health: string;
  competition_level: string;
  best_opportunities: LocalMarketOpportunity[];
  strategic_recommendations: string[];
}

interface EVESystem {
  name: string;
  competition: string;
  specialization: string;
  region: string;
  security: string;
  description: string;
}

export default function Dashboard() {
  const {
    marketData,
    tradingSignals,
    portfolioItems,
    systemAnalysis,
    selectedSystem,
    isConnected,
    lastUpdate,
    loading,
    error,
    refreshAllData,
    changeSystem,
  } = useDataFetcher();

  const [activeTab, setActiveTab] = useState<
    "overview" | "local" | "signals" | "portfolio" | "jump_planning"
  >("overview");
  const [isSystemDropdownOpen, setIsSystemDropdownOpen] = useState(false);
  const [systemSearchTerm, setSystemSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Comprehensive EVE systems database
  const eveSystems: EVESystem[] = [
    // Major Trading Hubs
    {
      name: "Jita",
      competition: "Very High",
      specialization: "Everything",
      region: "The Forge",
      security: "0.9",
      description: "Primary trading hub, highest volume",
    },
    {
      name: "Amarr",
      competition: "High",
      specialization: "Minerals, Ships",
      region: "Domain",
      security: "0.9",
      description: "Empire trading hub, good for minerals",
    },
    {
      name: "Dodixie",
      competition: "Medium",
      specialization: "Minerals, Components",
      region: "Essence",
      security: "0.9",
      description: "Gallente hub, component trading",
    },
    {
      name: "Rens",
      competition: "Medium",
      specialization: "Minerals, Ammunition",
      region: "Heimatar",
      security: "0.9",
      description: "Minmatar hub, ammunition focus",
    },
    {
      name: "Hek",
      competition: "Medium",
      specialization: "Minerals, Drones",
      region: "Metropolis",
      security: "0.9",
      description: "Minmatar hub, drone trading",
    },

    // Secondary Trading Centers
    {
      name: "Perimeter",
      competition: "Medium",
      specialization: "Everything",
      region: "The Forge",
      security: "0.9",
      description: "Jita alternative, less competition",
    },
    {
      name: "New Caldari",
      competition: "Medium",
      specialization: "Ships, Modules",
      region: "The Forge",
      security: "0.9",
      description: "Caldari industrial hub",
    },
    {
      name: "Old Man Star",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "Essence",
      security: "0.4",
      description: "Low sec trading, PvP supplies",
    },
    {
      name: "Oursulaert",
      competition: "Medium",
      specialization: "Minerals, Components",
      region: "Essence",
      security: "0.9",
      description: "Gallente industrial hub",
    },
    {
      name: "Niarja",
      competition: "Medium",
      specialization: "Minerals, Ships",
      region: "Domain",
      security: "0.9",
      description: "Amarr industrial hub",
    },

    // Industrial Hubs
    {
      name: "Motsu",
      competition: "Low",
      specialization: "Minerals, Components",
      region: "Essence",
      security: "0.9",
      description: "Gallente industrial center",
    },
    {
      name: "Sakenta",
      competition: "Low",
      specialization: "Minerals, Ships",
      region: "Domain",
      security: "0.9",
      description: "Amarr industrial center",
    },
    {
      name: "Urlen",
      competition: "Low",
      specialization: "Minerals, Ammunition",
      region: "Heimatar",
      security: "0.9",
      description: "Minmatar industrial center",
    },
    {
      name: "Tama",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "The Forge",
      security: "0.4",
      description: "Low sec trading hub",
    },
    {
      name: "Stacmon",
      competition: "Low",
      specialization: "Minerals, Components",
      region: "Essence",
      security: "0.9",
      description: "Gallente industrial hub",
    },

    // Regional Hubs
    {
      name: "Alikara",
      competition: "Low",
      specialization: "Minerals",
      region: "Essence",
      security: "0.9",
      description: "Regional trading center",
    },
    {
      name: "Auga",
      competition: "Low",
      specialization: "Minerals",
      region: "Heimatar",
      security: "0.9",
      description: "Regional trading center",
    },
    {
      name: "Balle",
      competition: "Low",
      specialization: "Minerals",
      region: "Metropolis",
      security: "0.9",
      description: "Regional trading center",
    },
    {
      name: "Couster",
      competition: "Low",
      specialization: "Minerals",
      region: "The Forge",
      security: "0.9",
      description: "Regional trading center",
    },
    {
      name: "Dodenvier",
      competition: "Low",
      specialization: "Minerals",
      region: "Essence",
      security: "0.9",
      description: "Regional trading center",
    },

    // Specialized Markets
    {
      name: "Aunenen",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "Essence",
      security: "0.4",
      description: "Low sec PvP supplies",
    },
    {
      name: "Eram",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "Domain",
      security: "0.4",
      description: "Low sec PvP supplies",
    },
    {
      name: "Fliet",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "Heimatar",
      security: "0.4",
      description: "Low sec PvP supplies",
    },
    {
      name: "Gultratren",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "Metropolis",
      security: "0.4",
      description: "Low sec PvP supplies",
    },
    {
      name: "Hikkoken",
      competition: "Low",
      specialization: "PvP Supplies",
      region: "The Forge",
      security: "0.4",
      description: "Low sec PvP supplies",
    },
  ];

  // Filter systems based on search term
  const filteredSystems = eveSystems.filter(
    (system) =>
      system.name.toLowerCase().includes(systemSearchTerm.toLowerCase()) ||
      system.region.toLowerCase().includes(systemSearchTerm.toLowerCase()) ||
      system.specialization
        .toLowerCase()
        .includes(systemSearchTerm.toLowerCase())
  );

  // Get current system info
  const currentSystem =
    eveSystems.find((s) => s.name === selectedSystem) || eveSystems[0];

  // Reset pagination when system changes
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedSystem]);

  const getProfitClass = (value: number) => {
    if (value > 0) return "profit-positive";
    if (value < 0) return "profit-negative";
    return "profit-neutral";
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "STRONG BUY":
        return "text-eve-success";
      case "BUY":
        return "text-eve-success";
      case "HOLD":
        return "text-eve-warning";
      case "SELL":
        return "text-eve-danger";
      default:
        return "text-eve-light";
    }
  };

  const getOpportunityTypeColor = (type: string) => {
    switch (type) {
      case "Undersupplied":
        return "text-eve-success";
      case "Oversupplied":
        return "text-eve-warning";
      case "Arbitrage":
        return "text-eve-highlight";
      default:
        return "text-eve-light";
    }
  };

  const getCompetitionColor = (level: string) => {
    switch (level) {
      case "Very High":
        return "text-eve-danger";
      case "High":
        return "text-eve-warning";
      case "Medium":
        return "text-eve-highlight";
      case "Low":
        return "text-eve-success";
      default:
        return "text-eve-light";
    }
  };

  const getSecurityColor = (security: string) => {
    const sec = parseFloat(security);
    if (sec >= 0.8) return "text-eve-success";
    if (sec >= 0.5) return "text-eve-warning";
    return "text-eve-danger";
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest(".system-dropdown")) {
        setIsSystemDropdownOpen(false);
      }
    };

    if (isSystemDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isSystemDropdownOpen]);

  // Pagination functions
  const totalPages = systemAnalysis
    ? Math.ceil(systemAnalysis.best_opportunities.length / itemsPerPage)
    : 0;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentOpportunities = systemAnalysis
    ? systemAnalysis.best_opportunities.slice(startIndex, endIndex)
    : [];

  const goToPage = (page: number) => {
    setCurrentPage(page);
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Reset to page 1 when system changes
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedSystem]);

  // Add helper function for transport cost display
  const getTransportCostDisplay = (cost: number) => {
    if (cost === 0) return "Local";
    return `${cost.toLocaleString()} ISK`;
  };

  const getNetProfitDisplay = (
    grossProfit: number,
    transportCost: number,
    buyPrice: number
  ) => {
    const netProfit = grossProfit - transportCost / buyPrice;
    return (netProfit * 100).toFixed(1);
  };

  return (
    <div className="min-h-screen bg-eve-dark text-eve-light">
      {/* Header */}
      <header className="bg-eve-primary border-b border-eve-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Rocket className="h-8 w-8 text-eve-highlight" />
              <h1 className="text-xl font-eve font-bold">EVE Trading System</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div
                className={`flex items-center space-x-2 ${
                  isConnected ? "text-eve-success" : "text-eve-danger"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? "bg-eve-success" : "bg-eve-danger"
                  }`}
                ></div>
                <span className="text-sm">
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
              <button className="eve-button flex items-center space-x-2">
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </button>
              <button className="eve-button">
                <Settings className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* System Selector */}
      <div className="bg-eve-secondary border-b border-eve-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <MapPin className="h-5 w-5 text-eve-highlight" />
            <span className="text-sm font-medium">Target System:</span>

            {/* Searchable System Dropdown */}
            <div className="relative system-dropdown">
              <button
                onClick={() => setIsSystemDropdownOpen(!isSystemDropdownOpen)}
                className="eve-input text-sm flex items-center justify-between min-w-[300px]"
              >
                <span>{selectedSystem}</span>
                <ChevronDown
                  className={`h-4 w-4 transition-transform ${
                    isSystemDropdownOpen ? "rotate-180" : ""
                  }`}
                />
              </button>

              {isSystemDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-eve-secondary border border-eve-accent rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
                  {/* Search Input */}
                  <div className="p-3 border-b border-eve-accent">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-eve-light/50" />
                      <input
                        type="text"
                        placeholder="Search systems..."
                        value={systemSearchTerm}
                        onChange={(e) => setSystemSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-eve-primary border border-eve-accent rounded text-sm text-eve-light placeholder-eve-light/50 focus:outline-none focus:border-eve-highlight"
                        autoFocus
                      />
                      {systemSearchTerm && (
                        <button
                          onClick={() => setSystemSearchTerm("")}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-eve-light/50 hover:text-eve-light"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* System List */}
                  <div className="py-1">
                    {filteredSystems.map((system) => (
                      <button
                        key={system.name}
                        onClick={() => {
                          changeSystem(system.name);
                          setIsSystemDropdownOpen(false);
                          setSystemSearchTerm("");
                        }}
                        className={`w-full px-4 py-3 text-left hover:bg-eve-primary transition-colors ${
                          selectedSystem === system.name
                            ? "bg-eve-highlight text-eve-dark"
                            : "text-eve-light"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{system.name}</div>
                            <div className="text-xs text-eve-light/70">
                              {system.region} • {system.specialization}
                            </div>
                          </div>
                          <div className="text-right">
                            <div
                              className={`text-xs font-medium ${getCompetitionColor(
                                system.competition
                              )}`}
                            >
                              {system.competition}
                            </div>
                            <div
                              className={`text-xs ${getSecurityColor(
                                system.security
                              )}`}
                            >
                              {system.security}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}

                    {filteredSystems.length === 0 && (
                      <div className="px-4 py-3 text-eve-light/50 text-sm">
                        No systems found matching "{systemSearchTerm}"
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center space-x-2 text-sm">
              <Target className="h-4 w-4 text-eve-highlight" />
              <span>Specialization: {currentSystem.specialization}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm">
              <Shield className="h-4 w-4 text-eve-highlight" />
              <span className={getSecurityColor(currentSystem.security)}>
                Security: {currentSystem.security}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-eve-secondary border-b border-eve-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: "overview", label: "Overview", icon: BarChart3 },
              { id: "local", label: "Local Market", icon: MapPin },
              { id: "signals", label: "AI Signals", icon: Zap },
              { id: "portfolio", label: "Portfolio", icon: DollarSign },
              { id: "jump_planning", label: "Jump Planning", icon: Navigation },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? "border-eve-highlight text-eve-highlight"
                      : "border-transparent text-eve-light/70 hover:text-eve-light"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "overview" && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="eve-card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-eve-light/70">
                      Total Portfolio Value
                    </p>
                    <p className="text-2xl font-bold text-eve-success">
                      1,247,500 ISK
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-eve-success" />
                </div>
                <div className="mt-2">
                  <span className="text-sm profit-positive">+12.5%</span>
                  <span className="text-sm text-eve-light/70 ml-2">
                    vs yesterday
                  </span>
                </div>
              </div>

              <div className="eve-card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-eve-light/70">
                      Local Opportunities
                    </p>
                    <p className="text-2xl font-bold text-eve-highlight">
                      {systemAnalysis?.total_opportunities || 0}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-eve-highlight" />
                </div>
                <div className="mt-2">
                  <span className="text-sm text-eve-light/70">
                    in {selectedSystem}
                  </span>
                </div>
              </div>

              <div className="eve-card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-eve-light/70">
                      Avg Profit Margin
                    </p>
                    <p className="text-2xl font-bold text-eve-success">
                      {systemAnalysis
                        ? `${(systemAnalysis.avg_profit_margin * 100).toFixed(
                            1
                          )}%`
                        : "0%"}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-eve-success" />
                </div>
                <div className="mt-2">
                  <span className="text-sm text-eve-light/70">
                    Market Health: {systemAnalysis?.market_health}
                  </span>
                </div>
              </div>

              <div className="eve-card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-eve-light/70">
                      Competition Level
                    </p>
                    <p
                      className={`text-2xl font-bold ${getCompetitionColor(
                        systemAnalysis?.competition_level || ""
                      )}`}
                    >
                      {systemAnalysis?.competition_level || "Unknown"}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-eve-highlight" />
                </div>
                <div className="mt-2">
                  <span className="text-sm text-eve-light/70">
                    Market Activity
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <div className="eve-card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">
                    Top Local Opportunities
                  </h2>
                  <Star className="h-5 w-5 text-eve-highlight" />
                </div>
                <div className="space-y-3">
                  {systemAnalysis?.best_opportunities
                    .slice(0, 5)
                    .map((opp, index) => (
                      <div
                        key={opp.type_id}
                        className="border border-eve-accent rounded p-3"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{opp.item_name}</p>
                            <p className="text-sm text-eve-light/70">
                              {opp.opportunity_type} • {opp.local_demand} demand
                            </p>
                          </div>
                          <div className="text-right">
                            <p
                              className={`font-semibold ${getRecommendationColor(
                                opp.recommendation
                              )}`}
                            >
                              {opp.recommendation}
                            </p>
                            <p className="text-sm profit-positive">
                              {(opp.profit_margin * 100).toFixed(1)}% profit
                            </p>
                          </div>
                        </div>
                        <div className="mt-2 text-sm text-eve-light/70">
                          Buy: {opp.current_buy_price.toLocaleString()} ISK •
                          Sell: {opp.current_sell_price.toLocaleString()} ISK
                        </div>
                        <div className="mt-1 text-xs text-eve-highlight">
                          📍 Sell in: {opp.sell_location || "Local"} • 💰 Net:{" "}
                          {getNetProfitDisplay(
                            opp.profit_margin,
                            opp.transport_cost || 0,
                            opp.current_buy_price
                          )}
                          %
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              <div className="eve-card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">
                    Strategic Recommendations
                  </h2>
                  <Globe className="h-5 w-5 text-eve-highlight" />
                </div>
                <div className="space-y-3">
                  {systemAnalysis?.strategic_recommendations
                    .slice(0, 8)
                    .map((rec, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 rounded-full bg-eve-highlight mt-2 flex-shrink-0"></div>
                        <p className="text-sm">{rec}</p>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </>
        )}

        {activeTab === "local" && systemAnalysis && (
          <div className="space-y-8">
            {/* System Overview */}
            <div className="eve-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  Local Market Analysis: {systemAnalysis.system_name}
                </h2>
                <div className="flex items-center space-x-4 text-sm">
                  <span
                    className={`px-2 py-1 rounded ${getCompetitionColor(
                      systemAnalysis.competition_level
                    )}`}
                  >
                    {systemAnalysis.competition_level} Competition
                  </span>
                  <span className="px-2 py-1 rounded bg-eve-success text-eve-dark">
                    {systemAnalysis.market_health} Health
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-eve-highlight">
                    {systemAnalysis.total_opportunities}
                  </p>
                  <p className="text-sm text-eve-light/70">Opportunities</p>
                </div>
                <div>
                  <p className="text-2xl font-bold profit-positive">
                    {(systemAnalysis.avg_profit_margin * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm text-eve-light/70">Avg Profit Margin</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-eve-light">
                    {systemAnalysis.best_opportunities.length}
                  </p>
                  <p className="text-sm text-eve-light/70">Top Opportunities</p>
                </div>
              </div>
            </div>

            {/* Local Opportunities Table */}
            <div className="eve-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  Local Market Opportunities
                </h2>
                <span className="text-sm text-eve-light/70">
                  Last updated: {lastUpdate}
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="eve-table">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Buy Price</th>
                      <th>Sell Price</th>
                      <th>Profit %</th>
                      <th>Sell Location</th>
                      <th>Transport Cost</th>
                      <th>Net Profit %</th>
                      <th>Demand</th>
                      <th>Supply</th>
                      <th>Type</th>
                      <th>Score</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentOpportunities.map((opp) => (
                      <tr key={opp.type_id}>
                        <td className="font-medium">{opp.item_name}</td>
                        <td>{opp.current_buy_price.toLocaleString()} ISK</td>
                        <td>{opp.current_sell_price.toLocaleString()} ISK</td>
                        <td className="profit-positive">
                          {(opp.profit_margin * 100).toFixed(1)}%
                        </td>
                        <td className="font-medium text-eve-highlight">
                          {opp.sell_location || "Local"}
                        </td>
                        <td className="text-sm">
                          {getTransportCostDisplay(opp.transport_cost || 0)}
                        </td>
                        <td className="profit-positive">
                          {getNetProfitDisplay(
                            opp.profit_margin,
                            opp.transport_cost || 0,
                            opp.current_buy_price
                          )}
                          %
                        </td>
                        <td
                          className={
                            opp.local_demand === "High"
                              ? "text-eve-success"
                              : "text-eve-light"
                          }
                        >
                          {opp.local_demand}
                        </td>
                        <td
                          className={
                            opp.local_supply === "High"
                              ? "text-eve-warning"
                              : "text-eve-light"
                          }
                        >
                          {opp.local_supply}
                        </td>
                        <td
                          className={getOpportunityTypeColor(
                            opp.opportunity_type
                          )}
                        >
                          {opp.opportunity_type}
                        </td>
                        <td className="font-medium">{opp.score.toFixed(2)}</td>
                        <td
                          className={getRecommendationColor(opp.recommendation)}
                        >
                          {opp.recommendation}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6">
                  <div className="text-sm text-eve-light/70">
                    Showing {startIndex + 1}-
                    {Math.min(
                      endIndex,
                      systemAnalysis.best_opportunities.length
                    )}{" "}
                    of {systemAnalysis.best_opportunities.length} opportunities
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={goToPreviousPage}
                      disabled={currentPage === 1}
                      className="eve-button px-3 py-1 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>

                    <div className="flex items-center space-x-1">
                      {Array.from(
                        { length: Math.min(5, totalPages) },
                        (_, i) => {
                          let pageNum;
                          if (totalPages <= 5) {
                            pageNum = i + 1;
                          } else if (currentPage <= 3) {
                            pageNum = i + 1;
                          } else if (currentPage >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                          } else {
                            pageNum = currentPage - 2 + i;
                          }

                          return (
                            <button
                              key={pageNum}
                              onClick={() => goToPage(pageNum)}
                              className={`px-3 py-1 text-sm rounded ${
                                currentPage === pageNum
                                  ? "bg-eve-highlight text-eve-dark"
                                  : "bg-eve-primary text-eve-light hover:bg-eve-accent"
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        }
                      )}
                    </div>

                    <button
                      onClick={goToNextPage}
                      disabled={currentPage === totalPages}
                      className="eve-button px-3 py-1 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Action Plans */}
            <div className="eve-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Action Plans</h2>
                <ArrowUpDown className="h-5 w-5 text-eve-highlight" />
              </div>
              <div className="space-y-3">
                {currentOpportunities.slice(0, 5).map((opp) => (
                  <div
                    key={opp.type_id}
                    className="border border-eve-accent rounded p-3"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{opp.item_name}</p>
                        <p className="text-sm text-eve-light/70">
                          {opp.action_plan}
                        </p>
                        <p className="text-xs text-eve-highlight mt-1">
                          📍 Sell in: {opp.sell_location || "Local"} • 🚚
                          Transport:{" "}
                          {getTransportCostDisplay(opp.transport_cost || 0)} •
                          💰 Net Profit:{" "}
                          {getNetProfitDisplay(
                            opp.profit_margin,
                            opp.transport_cost || 0,
                            opp.current_buy_price
                          )}
                          %
                        </p>
                      </div>
                      <div className="text-right">
                        <p
                          className={`font-semibold ${getRecommendationColor(
                            opp.recommendation
                          )}`}
                        >
                          {opp.recommendation}
                        </p>
                        <p className="text-sm profit-positive">
                          {(opp.profit_margin * 100).toFixed(1)}% gross profit
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "signals" && (
          <div className="eve-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">AI Trading Signals</h2>
              <Activity className="h-5 w-5 text-eve-highlight animate-pulse" />
            </div>
            <div className="space-y-3">
              {tradingSignals.map((signal, index) => (
                <div
                  key={index}
                  className="border border-eve-accent rounded p-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{signal.item_name}</p>
                      <p className="text-sm text-eve-light/70">
                        {signal.action} • {(signal.confidence * 100).toFixed(1)}
                        % confidence
                      </p>
                      {signal.buy_location && signal.sell_location && (
                        <p className="text-xs text-eve-highlight mt-1">
                          📍 Buy: {signal.buy_location} → Sell:{" "}
                          {signal.sell_location}
                        </p>
                      )}
                      {signal.action_plan && (
                        <p className="text-xs text-eve-light/70 mt-1">
                          {signal.action_plan}
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      <p
                        className={`font-semibold ${
                          signal.action === "BUY"
                            ? "text-eve-success"
                            : signal.action === "SELL"
                            ? "text-eve-danger"
                            : "text-eve-warning"
                        }`}
                      >
                        {signal.action}
                      </p>
                      <p className="text-sm profit-positive">
                        {signal.price.toLocaleString()} ISK
                      </p>
                      {signal.net_profit_margin &&
                        signal.net_profit_margin > 0 && (
                          <p className="text-xs profit-positive">
                            {(signal.net_profit_margin * 100).toFixed(1)}% net
                            profit
                          </p>
                        )}
                    </div>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-xs text-eve-light/70">
                    <span>
                      {new Date(signal.timestamp).toLocaleTimeString()}
                    </span>
                    <div className="flex items-center space-x-2">
                      {signal.transport_cost && signal.transport_cost > 0 && (
                        <span className="text-eve-warning">
                          🚚 {signal.transport_cost.toLocaleString()} ISK
                        </span>
                      )}
                      {signal.signal_type && (
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            signal.signal_type === "EXPORT"
                              ? "bg-eve-success text-eve-dark"
                              : signal.signal_type === "IMPORT"
                              ? "bg-eve-highlight text-eve-dark"
                              : signal.signal_type === "ARBITRAGE"
                              ? "bg-eve-warning text-eve-dark"
                              : "bg-eve-accent text-eve-light"
                          }`}
                        >
                          {signal.signal_type}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "portfolio" && (
          <div className="eve-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Portfolio</h2>
              <Eye className="h-5 w-5 text-eve-light/70" />
            </div>
            <div className="overflow-x-auto">
              <table className="eve-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Avg Price</th>
                    <th>Current Price</th>
                    <th>Unrealized P&L</th>
                    <th>P&L %</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioItems.map((item) => (
                    <tr key={item.type_id}>
                      <td className="font-medium">{item.item_name}</td>
                      <td>{item.quantity.toLocaleString()}</td>
                      <td>{item.avg_price.toFixed(2)} ISK</td>
                      <td>{item.current_price.toFixed(2)} ISK</td>
                      <td className={getProfitClass(item.unrealized_pnl)}>
                        {item.unrealized_pnl > 0 ? "+" : ""}
                        {item.unrealized_pnl.toLocaleString()} ISK
                      </td>
                      <td className={getProfitClass(item.unrealized_pnl_pct)}>
                        {item.unrealized_pnl_pct > 0 ? "+" : ""}
                        {item.unrealized_pnl_pct.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "jump_planning" && (
          <div className="space-y-6">
            {/* Jump Planning Header */}
            <div className="eve-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  Jump Planning & Transport Efficiency
                </h2>
                <Navigation className="h-5 w-5 text-eve-light/70" />
              </div>
              <p className="text-eve-light/70 mb-4">
                Calculate optimal transport routes and ship efficiency for your
                trading operations.
              </p>
            </div>

            {/* Route Analysis */}
            <div className="eve-card">
              <h3 className="text-md font-semibold mb-4">Route Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Origin System
                  </label>
                  <select className="eve-input w-full">
                    <option value="Jita">Jita</option>
                    <option value="Amarr">Amarr</option>
                    <option value="Dodixie">Dodixie</option>
                    <option value="Rens">Rens</option>
                    <option value="Hek">Hek</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Destination System
                  </label>
                  <select className="eve-input w-full">
                    <option value="Amarr">Amarr</option>
                    <option value="Jita">Jita</option>
                    <option value="Dodixie">Dodixie</option>
                    <option value="Rens">Rens</option>
                    <option value="Hek">Hek</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Cargo Volume (m³)
                  </label>
                  <input
                    type="number"
                    className="eve-input w-full"
                    placeholder="500000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Item Name
                  </label>
                  <input
                    type="text"
                    className="eve-input w-full"
                    placeholder="Warrior II"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Quantity
                  </label>
                  <input
                    type="number"
                    className="eve-input w-full"
                    placeholder="1000"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Buy Price (ISK)
                  </label>
                  <input
                    type="number"
                    className="eve-input w-full"
                    placeholder="4050"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-eve-light/70 mb-2">
                    Sell Price (ISK)
                  </label>
                  <input
                    type="number"
                    className="eve-input w-full"
                    placeholder="5000"
                  />
                </div>
              </div>
              <button className="eve-button bg-eve-highlight hover:bg-eve-highlight/80">
                Calculate Route
              </button>
            </div>

            {/* Ship Comparison */}
            <div className="eve-card">
              <h3 className="text-md font-semibold mb-4">Ship Comparison</h3>
              <div className="overflow-x-auto">
                <table className="eve-table">
                  <thead>
                    <tr>
                      <th>Ship</th>
                      <th>Jumps</th>
                      <th>Fuel Cost</th>
                      <th>Insurance</th>
                      <th>Total Cost</th>
                      <th>Cost/m³</th>
                      <th>Travel Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="font-medium">Fenrir</td>
                      <td>3</td>
                      <td>22,500,000 ISK</td>
                      <td>1,500,000 ISK</td>
                      <td className="text-eve-success">24,000,000 ISK</td>
                      <td className="text-eve-success">20.00 ISK</td>
                      <td>15 min</td>
                    </tr>
                    <tr>
                      <td className="font-medium">Mammoth</td>
                      <td>4</td>
                      <td>20,000,000 ISK</td>
                      <td>1,000,000 ISK</td>
                      <td>21,000,000 ISK</td>
                      <td>33.87 ISK</td>
                      <td>20 min</td>
                    </tr>
                    <tr>
                      <td className="font-medium">Occator</td>
                      <td>3</td>
                      <td>18,000,000 ISK</td>
                      <td>800,000 ISK</td>
                      <td>18,800,000 ISK</td>
                      <td>58.75 ISK</td>
                      <td>15 min</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Transport Efficiency */}
            <div className="eve-card">
              <h3 className="text-md font-semibold mb-4">
                Transport Efficiency Analysis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-sm text-eve-light/70">Gross Profit</p>
                  <p className="text-xl font-bold text-eve-success">
                    950,000 ISK
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-eve-light/70">Transport Cost</p>
                  <p className="text-xl font-bold text-eve-warning">
                    24,000,000 ISK
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-eve-light/70">Net Profit</p>
                  <p className="text-xl font-bold text-eve-danger">
                    -23,050,000 ISK
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-eve-light/70">Profit Margin</p>
                  <p className="text-xl font-bold text-eve-danger">-569.1%</p>
                </div>
              </div>
              <div className="bg-eve-dark/50 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Recommendation</h4>
                <p className="text-eve-light/70">
                  This trade is not profitable due to high transport costs.
                  Consider finding items with higher profit margins or shorter
                  transport distances.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
