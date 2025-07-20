
# 🤖 AI-Powered EVE Online Trading Agent (Learning Project)

This is a personal learning project to build an AI agent that simulates profitable trading decisions inside the **EVE Online** game universe. The project covers real-world concepts including Python programming, data collection from REST APIs, supervised learning, simulation systems, and reinforcement learning — all in the context of EVE Online's market economy.

---

## 📌 Project Goals

- ✅ Learn Python by building a real-world trading agent
- ✅ Fetch and process real-time data from the EVE Swagger Interface (ESI) API
- ✅ Train machine learning models to make buy/sell decisions
- ✅ Simulate market trades in a virtual environment
- ✅ Introduce reinforcement learning to create an autonomous agent

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **API**: EVE Swagger Interface (ESI)
- **Libraries**:
  - Data: `pandas`, `numpy`, `matplotlib`
  - ML: `scikit-learn`
  - RL: `stable-baselines3`, `gymnasium`, `torch`
- **Environment**: Jupyter or VS Code + `venv` / `conda`
- **Storage**: CSV, JSON

---

## 📁 Project Structure (Planned)

```bash
eve-ai-trading-bot/
├── data/                  # Raw & processed market data
├── notebooks/             # Jupyter notebooks for EDA and prototyping
├── scripts/               # Python scripts (data fetching, training, simulation)
├── models/                # Saved ML models
├── simulation/            # Custom trading simulator
├── rl_agent/              # Reinforcement learning agent & environment
├── README.md              # Project overview
└── eve-ai-trading-agent-prd.md  # Full product requirements document
```

---

## 🔧 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/your-username/eve-ai-trading-bot.git
cd eve-ai-trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔍 Current Status

- [x] Project scoped and PRD written
- [ ] ESI API integration & data fetcher script
- [ ] Basic ML model
- [ ] Trade simulation engine
- [ ] RL agent and reward environment

---

## 📚 Learning Resources

- [Real Python](https://realpython.com/)
- [EVE ESI API Docs](https://esi.evetech.net/ui/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/tutorial/index.html)
- [Spinning Up (OpenAI)](https://spinningup.openai.com)
- [David Silver’s RL Lectures](https://www.youtube.com/watch?v=2pWv7GOvuf0)

---

## ⚠️ Disclaimer

This bot is intended for **educational purposes only**. It does **not** interact with the game client and does **not** perform live trades. All trading actions are simulated. Use of automation in EVE Online may violate the EULA and can result in bans. This project avoids such actions by keeping everything offline and simulated.

---

## 📄 License

MIT License
