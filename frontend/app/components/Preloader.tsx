"use client";

import React from "react";
import { Rocket, Activity, Target, Zap, RefreshCw } from "lucide-react";

interface PreloaderProps {
  isLoading: boolean;
  message?: string;
  type?: "fullscreen" | "inline" | "overlay";
  size?: "sm" | "md" | "lg";
}

export const Preloader: React.FC<PreloaderProps> = ({
  isLoading,
  message = "Loading market data...",
  type = "inline",
  size = "md",
}) => {
  if (!isLoading) return null;

  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  const containerClasses = {
    fullscreen:
      "fixed inset-0 bg-eve-dark/95 z-50 flex items-center justify-center",
    inline: "flex items-center justify-center p-4",
    overlay:
      "absolute inset-0 bg-eve-dark/80 flex items-center justify-center rounded-lg",
  };

  const messageClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
  };

  return (
    <div className={containerClasses[type]}>
      <div className="text-center">
        {/* Animated EVE Logo */}
        <div className="relative mb-4">
          <div className="relative">
            <Rocket
              className={`${sizeClasses[size]} text-eve-highlight animate-pulse mx-auto`}
            />
            <div className="absolute inset-0">
              <Rocket
                className={`${sizeClasses[size]} text-eve-highlight/30 animate-ping mx-auto`}
              />
            </div>
          </div>

          {/* Orbiting indicators */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative w-16 h-16">
              <Activity className="absolute top-0 left-1/2 transform -translate-x-1/2 w-3 h-3 text-eve-success animate-spin" />
              <Target className="absolute top-1/2 right-0 transform translate-x-1/2 w-3 h-3 text-eve-highlight animate-pulse" />
              <Zap className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-3 h-3 text-eve-warning animate-bounce" />
              <RefreshCw className="absolute top-1/2 left-0 transform -translate-x-1/2 w-3 h-3 text-eve-light animate-spin" />
            </div>
          </div>
        </div>

        {/* Loading message */}
        <div className="space-y-2">
          <p className={`${messageClasses[size]} text-eve-light font-medium`}>
            {message}
          </p>

          {/* Progress dots */}
          <div className="flex items-center justify-center space-x-1">
            <div className="w-2 h-2 bg-eve-highlight rounded-full animate-bounce"></div>
            <div
              className="w-2 h-2 bg-eve-highlight rounded-full animate-bounce"
              style={{ animationDelay: "0.1s" }}
            ></div>
            <div
              className="w-2 h-2 bg-eve-highlight rounded-full animate-bounce"
              style={{ animationDelay: "0.2s" }}
            ></div>
          </div>
        </div>

        {/* Loading bar */}
        <div className="mt-4 w-48 h-1 bg-eve-accent rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-eve-highlight to-eve-success rounded-full animate-pulse"></div>
        </div>

        {/* Status indicators */}
        <div className="mt-4 flex items-center justify-center space-x-4 text-xs text-eve-light/70">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-eve-success rounded-full animate-pulse"></div>
            <span>Market Data</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-eve-highlight rounded-full animate-pulse"></div>
            <span>Analysis</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-eve-warning rounded-full animate-pulse"></div>
            <span>Signals</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Specialized preloader components
export const MarketDataPreloader: React.FC<{ isLoading: boolean }> = ({
  isLoading,
}) => (
  <Preloader
    isLoading={isLoading}
    message="Analyzing market opportunities..."
    type="inline"
    size="md"
  />
);

export const SystemAnalysisPreloader: React.FC<{
  isLoading: boolean;
  systemName: string;
}> = ({ isLoading, systemName }) => (
  <Preloader
    isLoading={isLoading}
    message={`Analyzing ${systemName} market data...`}
    type="inline"
    size="md"
  />
);

export const FullscreenPreloader: React.FC<{ isLoading: boolean }> = ({
  isLoading,
}) => (
  <Preloader
    isLoading={isLoading}
    message="Initializing EVE Trading System..."
    type="fullscreen"
    size="lg"
  />
);

export const OverlayPreloader: React.FC<{
  isLoading: boolean;
  message?: string;
}> = ({ isLoading, message = "Loading..." }) => (
  <Preloader isLoading={isLoading} message={message} type="overlay" size="md" />
);
