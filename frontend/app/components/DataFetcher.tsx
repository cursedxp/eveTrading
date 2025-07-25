"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

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
  signal_type?: string;
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
  sell_location?: string;
  transport_cost?: number;
  net_profit_margin?: number;
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

export const useDataFetcher = () => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([]);
  const [portfolioItems, setPortfolioItems] = useState<PortfolioItem[]>([]);
  const [systemAnalysis, setSystemAnalysis] = useState<SystemAnalysis | null>(
    null
  );
  const [selectedSystem, setSelectedSystem] = useState<string>("Jita");
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = "http://localhost:5000/api";

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      const response = await axios.get<ApiResponse<MarketData[]>>(
        `${API_BASE_URL}/market-data`
      );
      if (response.data.success) {
        setMarketData(response.data.data);
      }
    } catch (err) {
      console.error("Error fetching market data:", err);
      setError("Failed to fetch market data");
    } finally {
      setLoading(false);
    }
  };

  const fetchTradingSignals = async () => {
    try {
      setLoading(true);
      const response = await axios.get<ApiResponse<TradingSignal[]>>(
        `${API_BASE_URL}/trading-signals`
      );
      if (response.data.success) {
        setTradingSignals(response.data.data);
      }
    } catch (err) {
      console.error("Error fetching trading signals:", err);
      setError("Failed to fetch trading signals");
    } finally {
      setLoading(false);
    }
  };

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      const response = await axios.get<ApiResponse<PortfolioItem[]>>(
        `${API_BASE_URL}/portfolio`
      );
      if (response.data.success) {
        setPortfolioItems(response.data.data);
      }
    } catch (err) {
      console.error("Error fetching portfolio data:", err);
      setError("Failed to fetch portfolio data");
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemAnalysis = async (systemName: string = "Jita") => {
    try {
      setLoading(true);
      const response = await axios.get<ApiResponse<SystemAnalysis>>(
        `${API_BASE_URL}/system-analysis?system_name=${systemName}`
      );
      if (response.data.success) {
        setSystemAnalysis(response.data.data);
      }
    } catch (err) {
      console.error("Error fetching system analysis:", err);
      setError("Failed to fetch system analysis");
    } finally {
      setLoading(false);
    }
  };

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setIsConnected(response.status === 200);
    } catch (err) {
      setIsConnected(false);
    }
  };

  const refreshAllData = async () => {
    setError(null);
    await Promise.all([
      fetchMarketData(),
      fetchTradingSignals(),
      fetchPortfolioData(),
      fetchSystemAnalysis(selectedSystem),
      checkConnection(),
    ]);
    setLastUpdate(new Date().toLocaleTimeString());
  };

  const changeSystem = async (systemName: string) => {
    setSelectedSystem(systemName);
    await fetchSystemAnalysis(systemName);
  };

  useEffect(() => {
    // Initial data fetch
    refreshAllData();

    // Set up periodic refresh every 30 seconds
    const interval = setInterval(refreshAllData, 30000);

    return () => clearInterval(interval);
  }, [selectedSystem]);

  return {
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
    checkConnection,
    changeSystem,
  };
};
