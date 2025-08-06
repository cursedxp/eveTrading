import { useState, useCallback } from "react";
import { apiService } from "../services/apiService";

export const useDataFetcher = () => {
  // State management
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check connection status
  const checkConnection = useCallback(async () => {
    try {
      const connected = await apiService.checkHealth();
      setIsConnected(connected);
      if (connected) {
        setLastUpdate(new Date().toISOString());
      }
      return connected;
    } catch (error) {
      console.error("❌ Connection check failed:", error);
      setIsConnected(false);
      return false;
    }
  }, []);

  // Refresh all data
  const refreshAllData = useCallback(async (forceRefresh: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      
      // Just check connection for now
      await checkConnection();
      
      setLastUpdate(new Date().toISOString());
    } catch (error) {
      console.error("❌ Refresh failed:", error);
      setError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [checkConnection]);

  return {
    // State
    isConnected,
    lastUpdate,
    loading,
    error,

    // Functions
    refreshAllData,
    checkConnection,
  };
};