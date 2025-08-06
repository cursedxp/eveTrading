import axios from "axios";
import {
  ProfitableRoutesData,
  ApiResponse,
} from "../types/api";

const API_BASE_URL = ""; // Use relative URLs for Next.js API routes

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(
      `🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`
    );
    return config;
  },
  (error) => {
    console.error("❌ API Request Error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(
      "❌ API Response Error:",
      error.response?.status,
      error.message
    );
    return Promise.reject(error);
  }
);

// API Service Functions
export const apiService = {
  // Profitable Routes
  async fetchProfitableRoutes(): Promise<ProfitableRoutesData> {
    try {
      const response = await apiClient.get<ApiResponse<ProfitableRoutesData>>(
        "/api/profitable-routes"
      );

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error("Profitable routes API returned error");
      }
    } catch (error) {
      console.error("❌ Profitable routes fetch failed:", error);
      throw new Error("Failed to fetch profitable routes");
    }
  },

  // Health Check
  async checkHealth(): Promise<boolean> {
    try {
      const response = await apiClient.get("/api/health");
      return response.status === 200;
    } catch (error) {
      console.error("Health check failed:", error);
      return false;
    }
  },
};