// Helper function to format percentages to 2 digits maximum
export const formatPercentage = (value: number): string => {
  // VALIDATION: Handle unrealistic profit margins
  if (value > 50) {
    console.warn(
      `Unrealistic profit margin detected: ${value}% - capping at 50%`
    );
    value = 50;
  }

  if (value < 0) {
    console.warn(`Negative profit margin detected: ${value}% - setting to 0%`);
    value = 0;
  }

  if (value >= 100) {
    return Math.round(value).toString();
  } else if (value >= 10) {
    return value.toFixed(0);
  } else {
    return value.toFixed(1);
  }
};

// Helper function to show exact percentage without validation
export const formatExactPercentage = (value: number): string => {
  // Check if value is already a percentage (>= 1) or a decimal (< 1)
  const isAlreadyPercentage = value >= 1;

  if (isAlreadyPercentage) {
    // Value is already a percentage, don't multiply by 100
    if (value >= 100) {
      return Math.round(value).toString();
    } else if (value >= 10) {
      return value.toFixed(0);
    } else {
      return value.toFixed(1);
    }
  } else {
    // Value is a decimal, convert to percentage
    const percentage = value * 100;
    if (percentage >= 100) {
      return Math.round(percentage).toString();
    } else if (percentage >= 10) {
      return percentage.toFixed(0);
    } else {
      return percentage.toFixed(1);
    }
  }
};

// Helper function for transport cost display
export const getTransportCostDisplay = (cost: number) => {
  if (cost === 0) return "Local";
  return `${cost.toLocaleString()} ISK`;
};

// Helper function for net profit display
export const getNetProfitDisplay = (
  grossProfit: number,
  transportCost: number,
  buyPrice: number
) => {
  const netProfit = grossProfit - transportCost;
  const netProfitPercent = (netProfit / buyPrice) * 100;
  return formatPercentage(netProfitPercent);
};

// Helper function to get profit class for styling
export const getProfitClass = (value: number) => {
  if (value > 0) return "profit-positive";
  if (value < 0) return "profit-negative";
  return "profit-neutral";
};

// Helper function to get recommendation color
export const getRecommendationColor = (recommendation: string) => {
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

// Helper function to get opportunity type color
export const getOpportunityTypeColor = (type: string) => {
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

// Helper function to get competition color
export const getCompetitionColor = (level: string) => {
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

// Helper function to get security color
export const getSecurityColor = (security: string) => {
  const sec = parseFloat(security);
  if (sec >= 0.8) return "text-eve-success";
  if (sec >= 0.5) return "text-eve-warning";
  return "text-eve-danger";
};
