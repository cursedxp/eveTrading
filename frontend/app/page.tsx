"use client";

import React, { useState, useEffect } from "react";
import { useDataFetcher } from "./components/DataFetcher";
import { Preloader, FullscreenPreloader } from "./components/Preloader";
import { Header } from "./components/dashboard/Header";
import { ProfitableRoutesTab } from "./components/dashboard/tabs/ProfitableRoutesTab";
import { Package } from "lucide-react";

export default function Dashboard() {
  const {
    isConnected,
    lastUpdate,
    loading,
    refreshAllData,
  } = useDataFetcher();

  const [showUpdateNotification, setShowUpdateNotification] = useState(false);

  useEffect(() => {
    // Don't auto-load data on mount - let user select a system first
    console.log("📱 Dashboard mounted - waiting for user to select system");
  }, []);

  const handleRefresh = async () => {
    try {
      await refreshAllData(true); // Force refresh to bypass cache
      setShowUpdateNotification(true);
      setTimeout(() => setShowUpdateNotification(false), 3000);
    } catch (error) {
      console.error("Refresh failed:", error);
    }
  };

  return (
    <div className="min-h-screen bg-eve-dark text-eve-light">
      {/* Fullscreen Preloader for initial load */}
      <FullscreenPreloader isLoading={loading && !isConnected} />

      {/* Update Notification */}
      {showUpdateNotification && (
        <div className="fixed top-4 right-4 bg-eve-success text-eve-dark px-4 py-2 rounded-lg shadow-lg z-50 animate-in slide-in-from-right">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-eve-dark rounded-full animate-pulse"></div>
            <span className="font-medium">Data updated successfully!</span>
          </div>
        </div>
      )}

      {/* Header */}
      <Header
        isConnected={isConnected}
        lastUpdate={lastUpdate}
        loading={loading}
        onRefresh={handleRefresh}
      />

      {/* Navigation Tabs */}
      <div className="bg-eve-secondary border-b border-eve-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <div className="flex items-center space-x-2 py-4 px-1 border-b-2 border-eve-highlight text-eve-highlight font-medium text-sm">
              <Package className="h-4 w-4" />
              <span>Profitable Routes</span>
            </div>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ProfitableRoutesTab
          onRefresh={handleRefresh}
          loading={loading}
        />
      </main>
    </div>
  );
}
