# Pollen Python Agent

> **Comprehensive AI Agent Module for Pollen Ecosystem** — *Port 9000*

This Python module extends the TypeScript Pollen ecosystem with advanced AI capabilities:
- Local LLM integration (Ollama)
- Content generation (websites, mobile apps, media)
- Social media automation
- Wellness protocol execution
- Shadow accumulation & graduation ceremony

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  POLLEN ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TypeScript Core (existing)                                  │
│  ├── pollen-core (biometrics, prediction, therapy)          │
│  ├── pollen-bridge (Hive connection)                        │
│  ├── pollen-consensus (validation)                          │
│  ├── pollen-economics (tokens)                              │
│  └── pollen-python (this module) ◄── NEW                    │
│       └── Port 9000 FastAPI server                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
cd pollen-python
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Server runs on **port 9000**.

---

## Integration with TypeScript

```typescript
import { PythonAgentClient } from './pollen-python';

const pythonAgent = new PythonAgentClient({
  host: 'localhost',
  port: 9000,
  enabled: true
});

// Get status
const status = await pythonAgent.getStatus();

// Execute task
const result = await pythonAgent.executeTask('create_website', {
  title: 'My Portfolio',
  content: '...'
});
```

---

## API Endpoints

See [PYTHON_README.md](./PYTHON_README.md) for full API documentation.

---

## Features

| Feature | Description |
|---------|-------------|
| Wellness Agent | Biometric harvest, protocol execution |
| Creative Agent | Websites, apps, images, audio, video |
| Social Agent | Twitter, Instagram, TikTok, LinkedIn |
| Technical Agent | Code generation, IoT, 3D print prep |
| Admin Agent | Shadow wallet, graduation |

---

## License

MIT — Adrian Sortino (The Dude)
