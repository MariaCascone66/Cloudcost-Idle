# ☁️ CloudCost-Idle

Un plugin DevStack per:

1. 🧮 Stimare il costo delle VM accese
2. 💤 Rilevare VM inutilizzate ("idle")

## 🚀 Funzionalità

- Analizza le VM attive
- Calcola costo simulato basato su flavor e uptime
- Rileva VM con CPU bassa e uptime alto
- Dashboard web (Flask) con due tabelle

## 🛠️ Installazione

Nel tuo `local.conf`, aggiungi:
[[local|localrc]] enable_plugin cloudcost-idle https://github.com/tuo-user/cloudcost-idle

Poi esegui:

./stack.sh
