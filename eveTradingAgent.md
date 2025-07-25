
# 📘 PRD – AI-Powered EVE Online Trading Agent (Learning Project)

## 🧠 Purpose

This project is intended as a personal learning journey to build an AI agent capable of identifying and executing profitable trades within the EVE Online game universe. The goal is not only to explore artificial intelligence concepts such as data collection, supervised learning, and reinforcement learning but also to gain hands-on experience with Python, machine learning models, and API-driven trading logic through a game-based simulation.

## 🎯 Objectives

- Set up a local development environment for Python and essential libraries.
- Access and extract real market data from the EVE Swagger Interface (ESI) API.
- Train a simple machine learning model to classify profitable trades.
- Build a simulation engine to test decisions without impacting a live game account.
- Introduce reinforcement learning to train an agent to optimize trading strategies over time.
- Develop AI logic for autonomous item selection based on market risk/reward.

## 🔧 Key Features

| Feature | Description |
|---------|-------------|
| 📡 ESI API Integration | Connect to the official EVE Online ESI API to fetch market orders, item metadata, and regional trading data. |
| 🧮 Market Data Processor | Parse and clean API responses, calculate price differences, volume, margins, and arbitrage opportunities. |
| 🧠 ML Classifier | Train a supervised machine learning model to determine which items should be bought/sold based on market indicators. |
| 🧪 Trading Simulator | Simulate trading operations in a virtual environment to track decisions, profit/loss, and learn from outcomes. |
| 🤖 Reinforcement Learning Agent | Use RL algorithms like PPO or DQN to allow an agent to learn through trial and error in a simulated EVE market environment. |
| 📝 Logging & Reports | Generate logs and summary reports for model predictions, actions, and results. Optionally export to CSV. |

## 🧱 System Architecture

```
       +---------------------+
       |     ESI API         |
       +---------------------+
                |
         [Data Fetcher.py]
                |
         [Data Processor]
                |
         [Feature Engineering]
                |
         [ML Model / RL Agent]
                |
         [Trade Simulator]
                |
        [Reports / Visualization]
```

## 💡 Use Cases

1. **Fetch Data**: User runs a script to pull market order data from selected regions via the ESI API.
2. **Analyze Opportunities**: The system calculates key metrics such as price gaps and volume to detect profitable items.
3. **Train ML Model**: Based on historical decisions (or synthetic labels), the system trains a model to predict trade actions.
4. **Simulate Trades**: A virtual trade simulator mimics buy/sell actions and tracks portfolio performance.
5. **Reinforcement Agent** *(optional)*: An agent takes actions in the simulation, adjusting its strategy based on reward functions.

## ⚙️ Technical Requirements

| Component | Tech Stack |
|-----------|------------|
| Language | Python 3.10+ |
| API Access | EVE Swagger Interface (ESI) |
| Core Libraries | `requests`, `pandas`, `numpy`, `matplotlib`, `scikit-learn` |
| RL Libraries | `stable-baselines3`, `gymnasium`, `torch` |
| Environment | VS Code + virtualenv or conda, Jupyter optional |
| Data Storage | CSV or JSON for local logging |

## 🗂️ Required API Scopes (ESI)

| API Endpoint | Purpose |
|--------------|---------|
| `markets/{region_id}/orders/` | Get live buy/sell orders in specific regions |
| `market/prices/` | Get average market prices for all types |
| `universe/types/{type_id}/` | Get item names and metadata |
| (Optional) `characters/{character_id}/orders/` | If you want to connect to a live account |

> ❗ Authentication with a personal character is **optional** and not required for market browsing and simulation.

## 🧪 Simulated Agent Actions

- **Buy** item when predicted profitability is high and risk is low
- **Sell** item when target margin is reached
- **Hold** when no opportunity is deemed strong enough
- Evaluate performance using simulated cash balance and inventory log

## 📅 Roadmap

| Phase | Time | Deliverables |
|-------|------|--------------|
| Phase 1: Setup + API | 3–5 days | Python environment + Fetching ESI market data |
| Phase 2: Data Analysis | 4–7 days | Extract metrics (margin, volume, volatility) |
| Phase 3: ML Modeling | 7–10 days | Train a supervised classifier for buy/sell decisions |
| Phase 4: Simulation Engine | 5–7 days | Build a mock trading engine that logs results |
| Phase 5: RL Agent | 10–14 days | Use PPO/DQN to train agent on simulated trades |
| Phase 6: Review & Visualization | Ongoing | Log performance, visualize results (matplotlib or plotly) |

## 🚫 Risks and Constraints

| Risk | Mitigation |
|------|------------|
| API Rate Limiting (60 requests/min) | Use pagination and caching |
| No prior ML knowledge | Follow a tutorial-driven learning style, start with simple models |
| RL complexity | Start with supervised learning and rule-based logic first |
| Game ban policy | Only simulate trades locally, do **not** inject into the live game |
| Long training times | Limit scope, simulate using partial markets first |

## ✅ Success Criteria

- [ ] Successfully connect to and retrieve data from the EVE Swagger API
- [ ] Process and structure data for ML input
- [ ] Train a classifier that can recommend profitable trades
- [ ] Build a functioning simulation engine with cash balance and trade history
- [ ] Train and evaluate an RL agent that improves its trading decisions over time

## 📚 Resources

| Topic | Resource |
|-------|----------|
| Python Basics | [RealPython](https://realpython.com), [LearnPython.org](https://www.learnpython.org/) |
| ESI API Docs | [EVE ESI Swagger UI](https://esi.evetech.net/ui/) |
| ML Tutorials | [scikit-learn docs](https://scikit-learn.org/stable/tutorial/index.html), BTK Akademi (TR) |
| RL Basics | [Spinning Up by OpenAI](https://spinningup.openai.com), [David Silver’s RL Lectures](https://www.youtube.com/watch?v=2pWv7GOvuf0) |
