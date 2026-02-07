# Pollen AI Agent

> **Sovereign AI Agent for Terracare Ecosystem** — *Your Personal Hive Worker*

[![Version](https://img.shields.io/badge/version-v1.0.0--production--ready-green)]()
[![Seven Pillars](https://img.shields.io/badge/Seven%20Pillars-P5-blue)]()
[![License](https://img.shields.io/badge/license-MIT-yellow)]()

Pollen operates as your sovereign AI agent within the Terracare ecosystem. Spawned via Hive Consciousness and guided by Sofie AI intelligence, Pollen autonomously manages your wellness, creates content, handles social media, and develops technical solutions—all while maintaining complete data sovereignty through zero-knowledge encryption.

---

## 🌸 Core Capabilities

### 1. Wellness Agent
- **Biometric Harvesting**: HRV, movement, frequency exposure from Heartware
- **Protocol Execution**: Tai Chi forms, meditation timing, nutrition tracking
- **Proof Submission**: Encrypted proof-of-wellness to Hive for Honey rewards

### 2. Creative Agent
- **Websites**: HTML/CSS/JS generation
- **Mobile Apps**: React Native/Flutter scaffolds
- **Documents**: PDF/Markdown generation
- **Images**: Stable Diffusion integration
- **Video**: FFmpeg processing
- **Audio**: Frequency compositions (432Hz, 528Hz, etc.)

### 3. Social Agent
- **Autonomous Posting**: Twitter/X, Instagram, TikTok, LinkedIn
- **Smart Scheduling**: 3 posts/day optimal timing
- **Content Sourcing**: Wellness journey & creative output
- **Engagement Tracking**: Submitted to Hive for community value rewards

### 4. Technical Agent
- **Code Generation**: Multi-language, tested modules
- **IoT Management**: Smart home via Sofie-systems
- **3D Printing**: Harmonic-Balance architectural specs
- **Git Operations**: Repo management

### 5. Administrative Agent
- **Shadow Wallet**: Level 1 Honey accumulation
- **Graduation Ceremony**: Level 1→2 handoff at threshold
- **Task Scheduling**: Intelligent prioritization
- **Offline Queue**: Deferred execution

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/DudeAdrian/pollen.git
cd pollen

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start Pollen agent
python main.py
```

### Verify Installation

```bash
# Health check
curl http://localhost:9000/health

# View agent status
curl http://localhost:9000/status
```

---

## 📡 API Endpoints (Port 9000)

### Hive Integration

```http
POST /spawn
```
Hive initiation - spawns agent with bee role assignment.

### Task Execution

```http
POST /task/execute
Content-Type: application/json

{
  "task_type": "build_website",
  "payload": {"title": "My Portfolio", "content": "..."},
  "require_consent": true
}
```

### Content Creation

```http
POST /create
Content-Type: application/json

{
  "content_type": "website",
  "prompt": "Wellness Journey Portfolio",
  "style": "minimalist"
}
```

### Publishing

```http
POST /publish
Content-Type: application/json

{
  "creation_id": "web_123456",
  "platform": "twitter"
}
```

### Status & Monitoring

```http
GET /status
```
Returns: Shadow balance, pending tasks, creation queue, wellness summary

---

## 🏗️ Architecture

```
Pollen Agent/
├── main.py                    # FastAPI server (port 9000)
├── src/pollen/
│   ├── agent_core.py         # LLM integration (Ollama)
│   ├── spawner.py            # Hive WebSocket connection
│   ├── engines/
│   │   ├── wellness_engine.py    # Biometric harvest
│   │   ├── creator_engine.py     # Content generation
│   │   ├── social_manager.py     # Social media APIs
│   │   └── shadow_accumulator.py # Pre-wallet tracking
│   ├── utils/
│   │   └── encryptor.py      # Fernet/AES-256 encryption
│   └── consensus_client.py   # Hive consensus submission
├── data/
│   ├── vault/               # Encrypted creations
│   ├── queue/               # Pending tasks
│   └── cache/               # Temporary files
└── logs/                    # Agent logs
```

---

## 🔐 Security & Privacy

### Zero-Knowledge Architecture

- **All data encrypted locally** using Fernet (AES-128-CBC + HMAC)
- **Only proof hashes** sent to Hive (zero-knowledge)
- **Master key** never leaves device
- **Encrypted vault** for all creations
- **User consent required** for publishing

### Encryption Flow

```
User Data → Fernet Encryption → Local Storage (.enc)
                     ↓
              Proof Hash (SHA-256)
                     ↓
               Hive Consensus
                     ↓
              Ledger Rewards
```

---

## 🐝 Hive Integration

### Spawn Process

1. Pollen POSTs to `/spawn` with capabilities
2. Hive assigns bee role (Scout/Worker/Nurse/Guard)
3. WebSocket connection established
4. Agent receives tasks from Hive Consciousness

### Proof Submission

1. Activity completed (wellness, creative, etc.)
2. Data encrypted locally
3. Proof hash submitted to Hive
4. Hive validators reach consensus
5. Honey rewards issued via Ledger

---

## 💰 Shadow Accumulator (Level 1)

### Honey Tracking

| Activity Type | Base Value | Multiplier |
|--------------|------------|------------|
| Wellness Protocol | 10/min | 1.3x |
| Content Creation | 50-500 | 1.5x |
| Social Post | 25-100 | 1.2x |
| Code Generation | 30-200 | 1.4x |

### Graduation Threshold

- **Default**: 1000 Honey
- **Auto-graduation**: Optional (configurable)
- **Ceremony**: Wallet creation + balance transfer
- **Result**: Level 2 sovereign wallet

---

## 🎨 Content Creation Examples

### Generate Website

```bash
curl -X POST http://localhost:9000/create \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "website",
    "prompt": "Wellness Journey Portfolio",
    "options": {"template": "portfolio", "content": "My bio..."}
  }'
```

### Generate Mobile App

```bash
curl -X POST http://localhost:9000/create \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "mobile_app",
    "prompt": "Meditation Tracker",
    "options": {"platform": "react_native", "screens": ["Home", "Timer", "Stats"]}
  }'
```

### Generate Frequency Audio

```bash
curl -X POST http://localhost:9000/create \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "audio",
    "prompt": "Healing Frequency Composition",
    "options": {"frequencies": [432, 528, 639], "duration": 600}
  }'
```

---

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POLLEN_PORT` | API server port | 9000 |
| `HIVE_URL` | Hive endpoint | http://localhost:3000 |
| `SOFIE_URL` | Sofie AI endpoint | http://localhost:8000 |
| `OLLAMA_HOST` | Local LLM | http://localhost:11434 |
| `SHADOW_HONEY_THRESHOLD` | Graduation threshold | 1000 |
| `VAULT_PATH` | Encrypted storage | ./data/vault |

See `.env.example` for complete configuration.

---

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Test wellness engine
pytest tests/test_wellness.py -v

# Test creator engine
pytest tests/test_creator.py -v

# Integration test
pytest tests/test_integration.py -v
```

---

## 🐝 The Seven Pillars Alignment

Pollen operates primarily in **Pillar 5: Black Market Tactics** (Shadow/Participation)

- **Shadow Wallet**: Pre-on-chain accumulation
- **Participation Rewards**: All activities valued
- **Community Value**: Social contributions tracked
- **Sovereign Systems**: Zero-knowledge architecture

---

## 📞 Integration Points

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Hive | ws://localhost:3000 | Task receipt, consensus |
| Sofie | http://localhost:8000 | Intelligence guidance |
| Heartware | http://localhost:3001 | Biometric data |
| Ledger | http://localhost:8545 | Rewards, wallet |
| Ollama | http://localhost:11434 | Local LLM |

---

## 🚦 Feature Flags

Enable/disable capabilities via environment:

```bash
ENABLE_WELLNESS_AGENT=true
ENABLE_CREATIVE_AGENT=true
ENABLE_SOCIAL_AGENT=true
ENABLE_TECHNICAL_AGENT=true
ENABLE_ADMIN_AGENT=true
AUTO_EXECUTE_TASKS=false
REQUIRE_CONSENT_FOR_PUBLISH=true
```

---

## 📄 License

MIT — Created by Adrian Sortino ("The Dude")

> *"The swarm does not command. The swarm resonates."*  
> — S.O.F.I.E.

---

**Version**: v1.0.0-production-ready  
**Port**: 9000  
**Status**: Operational 🐝
