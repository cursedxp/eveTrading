// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// Profitable Routes Types
export interface ProfitableRoute {
  item_name: string;
  type_id: number;
  category: string;
  buy_system: string;
  sell_system: string;
  buy_price: number;
  sell_price: number;
  profit_margin: number;
  volume_24h: number;
  net_profit_percent: number;
  confidence_score: number;
  risk_level: string;
  route: string;
}

export interface ProfitableRoutesResponse {
  routes: ProfitableRoute[];
  summary: {
    total_routes: number;
    avg_profit_margin: number;
    total_volume: number;
    best_route: {
      item_name: string;
      profit_margin: number;
      route: string;
    };
  };
  categories: {
    [key: string]: {
      count: number;
      avg_profit: number;
      top_item: string;
    };
  };
}

export interface ProfitableRoutesData {
  success: boolean;
  data: ProfitableRoutesResponse;
  timestamp: string;
}