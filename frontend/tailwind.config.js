/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        eve: {
          primary: "#1a1a2e",
          secondary: "#16213e",
          accent: "#0f3460",
          highlight: "#e94560",
          success: "#00ff88",
          warning: "#ffaa00",
          danger: "#ff4444",
          dark: "#0f0f23",
          light: "#f8f9fa",
        },
      },
      fontFamily: {
        eve: ["Orbitron", "monospace"],
        sans: ["Inter", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        glow: "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        glow: {
          "0%": { boxShadow: "0 0 5px #e94560" },
          "100%": { boxShadow: "0 0 20px #e94560, 0 0 30px #e94560" },
        },
      },
    },
  },
  plugins: [],
};
