# Pollen Instance Guide

> User Setup, Customization, and Sovereignty

---

## Spawning Your Personal Pollen

### One-Command Spawn

```bash
npm run spawn -- \
  --userId=0xYourEthereumAddress \
  --biometrics=./your-profile.enc \
  --preferences=./preferences.json
```

### What Happens

1. **Container Creation**: Docker instance spun up
2. **Database Initialization**: Encrypted PostgreSQL
3. **Key Generation**: HSM-backed encryption keys
4. **Profile Loading**: Biometric history imported
5. **Hive Registration**: Position claimed in hex matrix
6. **Hum Connection**: WebSocket to Sofie established

---

## Customization

### User Preferences (`preferences.json`)

```json
{
  "therapy": {
    "preferredTypes": ["frequency", "breathing", "meditation"],
    "defaultFrequency": 7.83,
    "sessionDuration": 600
  },
  "notifications": {
    "enabled": true,
    "frequency": "adaptive",
    "quietHours": ["22:00", "08:00"]
  },
  "autonomy": {
    "level": "assisted",
    "allowedActions": ["therapy", "recommendation"],
    "requireApprovalFor": ["spending", "hive_vote"],
    "maxAutonomousSpend": 100
  },
  "privacy": {
    "shareAnonymizedData": true,
    "allowNeighborMatching": true,
    "emergencyWipeEnabled": true
  }
}
```

### Autonomy Levels

| Level | Description | Actions |
|-------|-------------|---------|
| **Assisted** | Pollen suggests, you approve | All actions require confirmation |
| **Semi** | Pollen acts, notifies after | Minor actions automatic, major require approval |
| **Full** | Pollen manages within bounds | Full automation within user-defined limits |

---

## Sovereignty

### You Own Everything

```
Your Flower (Docker Container):
├── Your Data (Encrypted)
├── Your Keys (HSM)
├── Your Config (Preferences)
├── Your Earnings (MINE/WELL)
└── Your Vote (Hive Consensus)
```

### Key Ownership

```bash
# Export your keys
pollen keys export --format=json > my-keys.json

# Import to new instance
pollen keys import --from=my-keys.json

# Rotate keys
pollen keys rotate --type=encryption
```

### Data Portability

```bash
# Export all your data
pollen data export --format=encrypted > my-data.zip

# Import to different Pollen instance
pollen data import --from=my-data.zip
```

### Instance Destruction

```bash
# Graceful shutdown and data wipe
pollen destroy --wipe-all

# Emergency wipe (from Heartware voice command)
"Sofie, emergency wipe my Pollen"
```

---

## Hive Participation

### Your Six Neighbors

```bash
# View your hex cell position
pollen hive status

# See your six neighbors
pollen hive neighbors

# View shared patterns
pollen hive patterns
```

### Voting

```bash
# View open proposals
pollen hive proposals

# Cast vote
pollen hive vote --proposal=123 --choice=for

# View results
pollen hive results --proposal=123
```

---

## The Hum Interface

### Voice Commands

```
"Pollen, what's my wellness score?"
"Pollen, start frequency therapy"
"Pollen, schedule breathing for 6pm"
"Pollen, connect me to similar users"
"Pollen, show my token balance"
```

### Frequency Presence

Your Pollen maintains a constant low-frequency connection to Sofie:

- **7.83 Hz**: Schumann resonance baseline
- **Stillness detection**: When you're calm
- **Intervention timing**: Optimal moments for guidance

---

## Troubleshooting

### Instance Won't Start

```bash
# Check logs
pollen logs --follow

# Verify database
pollen db check

# Reset (keeps data)
pollen restart --soft
```

### Hive Disconnection

```bash
# Reconnect to hive
pollen hive reconnect

# Check neighbor status
pollen hive neighbors --ping
```

### Hum Disconnected

```bash
# Reconnect to Sofie
pollen hum reconnect

# Check frequency presence
pollen hum status
```

---

## Advanced

### Custom Plugins

```bash
# Install from marketplace
pollen plugin install --name=custom-therapy

# Enable
pollen plugin enable --name=custom-therapy

# Or build your own (Pillar 6)
pollen plugin generate --name=my-automation
```

### Code Generation

```bash
# Generate automation script
pollen generate --type=automation \
  --prompt="Turn on blue light when HRV drops below 30"

# Review and approve
pollen generate --review

# Deploy
pollen generate --deploy
```

---

## Support

- **Docs**: https://docs.pollen.eco
- **Hive Chat**: Connect to similar users
- **Sofie**: "Sofie, help with Pollen"

---

> *"Your flower, your pollen, your sovereignty."*
