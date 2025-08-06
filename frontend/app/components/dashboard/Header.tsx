"use client";

import React from "react";
import { Rocket, Clock, RefreshCw, Settings, Brain } from "lucide-react";

interface HeaderProps {
  isConnected: boolean;
  lastUpdate: string;
  loading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isConnected,
  lastUpdate,
  loading,
  onRefresh,
}) => {
  return (
    <header className="bg-eve-primary border-b border-eve-accent">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <Rocket className="h-8 w-8 text-eve-highlight" />
            <h1 className="text-xl font-eve font-bold">EVE Trading System</h1>

            {/* AI Status Indicator */}
            <div className="flex items-center space-x-2 ml-4">
              {loading ? (
                <div className="flex items-center space-x-2 text-eve-highlight">
                  <Brain className="h-4 w-4 animate-pulse" />
                  <span className="text-sm font-medium">
                    🤖 AI Analysis Running...
                  </span>
                </div>
              ) : isConnected ? (
                <div className="flex items-center space-x-2 text-eve-success">
                  <Brain className="h-4 w-4" />
                  <span className="text-sm font-medium">
                    ✅ AI Backend Connected
                  </span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-eve-danger">
                  <Brain className="h-4 w-4" />
                  <span className="text-sm font-medium">
                    ❌ AI Backend Disconnected
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-eve-light/70">
              <Clock className="h-4 w-4" />
              <span>Last update: {lastUpdate || "Never"}</span>
            </div>
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
            <button
              onClick={onRefresh}
              disabled={loading}
              className="eve-button flex items-center space-x-2 bg-eve-highlight hover:bg-eve-highlight/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw
                className={`h-4 w-4 ${loading ? "animate-spin" : ""}`}
              />
              <span>{loading ? "Updating..." : "Refresh Data"}</span>
            </button>
            <button className="eve-button">
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
