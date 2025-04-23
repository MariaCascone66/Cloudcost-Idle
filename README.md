# ☁️ CloudCost-Idle Plugin

Un plugin DevStack per monitorare i costi stimati delle VM e identificare le istanze inattive.

## 🔧 Funzionalità

- 💸 Stima realistica del costo delle VM (basato su vCPU, RAM, disco, uptime)
- 🔍 Rilevamento VM inattive con basso uso CPU (<5%)
- 🌐 Dashboard web in Flask

## 🗂️ Struttura

```plaintext
app/
├── cost_estimator.py
├── idle_detector.py
└── dashboard.py
templates/
├── index.html
└── idle_modal.html
