# ☁️ CloudCost & Idle VM Detector

Un plugin DevStack che:
- Stima i costi delle VM basandosi su flavor e uptime 🧮
- Rileva VM accese ma inattive per risparmiare risorse 💤
- Mostra tutto via dashboard Flask 🎨

## ⚙️ Requisiti
- DevStack con utente `stack`
- Flask
- openstacksdk
- Python 3

## 🚀 Avvio Plugin

```bash
cd devstack
source openrc admin admin
./plugin.sh stack install
./plugin.sh stack post-config
