# 📚 CloudCost-Idle

CloudCost-Idle è un plugin **per OpenStack** che permette di:

- **Stimare il costo** delle VM attive (calcolato in base a CPU, RAM, disco e uptime reale).
- **Individuare le VM inattive** (Idle Detector) per ottimizzare il consumo delle risorse cloud.
- **Gestire automaticamente Floating IP** e **apertura della porta TCP 22** per il corretto funzionamento SSH.

È pensato per aiutare gli amministratori a **monitorare i costi** e **ridurre sprechi**, fornendo una dashboard **semplice** accessibile via browser.

---

## 🛠️ Strumenti utilizzati

- **Python 3**
- **Flask** (web server e dashboard)
- **OpenStackSDK** (`openstacksdk`) per comunicare con OpenStack
- **Paramiko** (SSH verso le VM per calcolo uptime reale)
- **Systemd** per il servizio di avvio automatico
- **DevStack** come ambiente OpenStack di test
- **HTML/CSS** semplici per la dashboard

---

## 🖥️ Tecnologie e linguaggi principali

| Tecnologia  | Ruolo |
| ----------- | ----- |
| Python      | Backend principale (Flask app, connessione OpenStack) |
| Flask       | Server web che espone le pagine della dashboard |
| Jinja2      | Template engine per HTML dinamico |
| Systemd     | Gestione del servizio cloudcost_idle.service |
| OpenStackSDK| Accesso API OpenStack: server, flavor, autenticazione |
| Paramiko    | Connessioni SSH verso VM per lettura uptime |

---

# 🚀 Installazione e Setup

### 1. Clona il repository
```bash
git clone https://github.com/MariaCascone66/Cloudcost-Idle.git
cd Cloudcost-Idle
```

---

### 2. Configura le variabili di ambiente OpenStack
Assicurati di esportare le variabili OpenStack nel terminale:
```bash
export OS_AUTH_URL=http://<tuo_auth_url>:5000/v3
export OS_PROJECT_NAME=<nome_progetto>
export OS_USERNAME=<nome_utente>
export OS_PASSWORD=<password>
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_REGION_NAME=RegionOne
```

---

### 3. Crea un ambiente virtuale Python
(dentro la cartella Cloudcost-Idle)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Installa le dipendenze
```bash
pip install -r requirements.txt
```

**Nota:** Assicurati che `requirements.txt` includa anche:
```text
openstacksdk
paramiko
flask
```

---

### 5. Avvia manualmente l'applicazione Flask per testare
```bash
python app/dashboard.py
```

Poi vai su:

> http://<IP_del_tuo_server>:8080

Vedrai la **Dashboard Costi**!  
Cliccando su "Mostra VM inattive" si aprirà la **modalità Idle Detector**.

---

### 6. (Opzionale) Installare come servizio systemd
Se vuoi che il plugin parta automaticamente:

- Copia il file `systemd/cloudcost_idle.service` in `/etc/systemd/system/`
- Ricarica systemd:

```bash
sudo systemctl daemon-reload
```

- Abilita il servizio all'avvio:

```bash
sudo systemctl enable cloudcost_idle.service
```

- Avvia il servizio:

```bash
sudo systemctl start cloudcost_idle.service
```

Controlla che stia funzionando:

```bash
sudo systemctl status cloudcost_idle.service
```

---

# 📋 Funzionalità principali

| Funzione | Dettaglio |
| -------- | --------- |
| **Dashboard principale** | Elenco VM attive con costi stimati |
| **Idle Detector** | Identifica VM con CPU usage simulato <10% |
| **Cost Estimator** | Calcola costi basati su vCPU, RAM, Disk, uptime reale |
| **SSH Integration** | Recupero uptime tramite SSH su porta 22 |
| **Floating IP Manager** | Assegna IP pubblico automaticamente se mancante |
| **Security Group Manager** | Apre la porta TCP 22 automaticamente se necessario |
| **Servizio systemd** | Avvio automatico all'accensione della macchina |

---

# ⚙️ Struttura del progetto

```plaintext
Cloudcost-Idle/
├── app/
│   ├── cost_estimator.py   # Stima costi VM
│   ├── idle_detector.py    # Rileva VM inattive
│   └── dashboard.py        # App Flask principale
├── templates/
│   ├── index.html          # Dashboard costi
│   └── idle_modal.html     # Modalità VM inattive
├── devstack/
│   ├── plugin.sh           # Script per DevStack
│   └── settings            # File di configurazione
├── systemd/
│   └── cloudcost_idle.service # Definizione servizio systemd
├── requirements.txt        # Dipendenze Python
└── README.md               # Questo file
```

---

# 📌 Note finali

- **DevStack** deve essere correttamente installato e funzionante.
- **Non serve modificare OpenStack internamente**: il plugin usa solo API ufficiali tramite OpenStackSDK.
- **Idle Detector** usa valori CPU simulati.  
  In futuro puoi collegarlo a Monasca, Gnocchi o metriche reali via API OpenStack per una rilevazione reale.

---

# 🎯 Perché usare CloudCost-Idle?

- Ti dà **immediatamente visibilità** su quanto ti stanno costando le VM.
- Ti aiuta a trovare **VM dimenticate o non usate**, risparmiando risorse.
- È **leggero**, **standalone**, **non modifica nulla** del core OpenStack.
- Si integra facilmente in **ambiente DevStack** o anche in un piccolo cloud privato.

---

# 🚨 Requisiti particolari

| Requisito | Dettaglio |
| --------- | --------- |
| **Chiave SSH privata** | Deve esistere in `~/.ssh/mykey` |
| **Floating IP** | Necessario per accedere via SSH alle VM |
| **Porta TCP 22** | Deve essere aperta nel Security Group. Il plugin la apre automaticamente se non presente |

---