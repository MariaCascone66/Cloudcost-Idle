Certo! Ecco un README aggiornato e completo per il tuo progetto **CloudWatcher**, che riflette tutte le funzionalità attuali (dashboard, tagging meteo, creazione VM da interfaccia, simulazione carichi, gestione progetti e quote, ecc.):

---

```markdown
# 🌤️ CloudWatcher

CloudWatcher è un plugin personalizzato per OpenStack progettato per fornire una **dashboard web interattiva** che consente di:

- 📊 Visualizzare l'utilizzo delle risorse (CPU, RAM) per ogni progetto
- 🌦️ Simulare condizioni "meteo" per ogni VM in base al carico (CPU)
- 🛠️ Creare nuove VM tramite un'interfaccia web con form dinamico
- 📌 Visualizzare metadati simulati (CPU, RAM, Disk) per ogni VM
- 🧠 Evidenziare tag visivi come "errore", "IP pubblico", o sicurezza "restricted"

---

## 🧰 Requisiti

- Python 3.8+
- OpenStack DevStack attivo e funzionante
- Accesso al cloud OpenStack tramite credenziali d'ambiente (`OS_AUTH_URL`, `OS_USERNAME`, etc.)
- Ambiente virtuale consigliato (`venv`)
- Flask + OpenStack SDK

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

---

## 🚀 Avvio dell'applicazione

### 1. Imposta le credenziali OpenStack

Assicurati di esportare tutte le variabili d’ambiente richieste, ad esempio:

```bash
export OS_AUTH_URL=http://localhost/identity
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=yourpassword
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

Puoi anche gestirle tramite `EnvironmentFile` se lanci l’app con systemd.

---

### 2. Avvia la webapp

La dashboard Flask gira sulla porta `5001` con `waitress`:

```bash
python quota_dashboard.py
```

Poi visita [http://localhost:5001](http://localhost:5001)

---

### 3. Avvia il meteo tagger

In parallelo alla dashboard, avvia lo script `weather_tagger.py` per aggiornare ogni minuto i metadati meteo e carichi simulati delle VM:

```bash
python weather_tagger.py
```

---

## ✨ Funzionalità principali

### Dashboard (`/`)
- Mostra tutte le VM attive con icone di stato:
  - 🚫 Errore
  - 🔒 Sicurezza "restricted"
  - 🌍 IP pubblico
  - 🌤️ Meteo simulato
- Visualizza CPU, RAM e Disk simulati
- Tabella con utilizzo risorse per progetto (`usato / quota`)

### Crea VM (`/create_vm`)
- Form con dropdown dinamici per immagini, flavor e network
- I metadati di carico (CPU, RAM, Disk) vengono simulati
- Meteo assegnato in base al carico CPU (dopo 2 minuti dalla creazione)

---

## 📁 Struttura del progetto

```
cloudwatcher/
│
├── quota_dashboard.py      # App Flask principale
├── weather_tagger.py       # Script per assegnare tag meteo e simulare carichi
├── openstack_data.py       # Funzioni per ottenere immagini, flavor, network
├── auth.py                 # Connessione a OpenStack tramite SDK
│
├── templates/
│   ├── index.html          # Dashboard principale
│   └── create_vm.html      # Form per creare VM
│
├── requirements.txt        # Dipendenze Python
└── README.md               # Questo file
```

---

## 🛡️ Sicurezza

- Le credenziali non sono salvate su file ma gestite tramite variabili d’ambiente.
- Nessun dato sensibile viene salvato nel codice o nel frontend.

---

## 🧪 Testing

Puoi testare rapidamente la creazione di VM tramite la form web e verificare che:
- I metadati `sim_cpu`, `sim_ram`, `sim_disk` siano visibili nella card
- Il meteo venga aggiornato correttamente dallo script ogni minuto
- I progetti visualizzino correttamente le quote
