# Cloudcost Idle

**Cloudcost Idle** è un plugin per ambienti **OpenStack** sviluppato per identificare e gestire le **istanze virtuali inattive**, stimarne il **costo di esercizio reale** e fornire strumenti di ottimizzazione tramite **riattivazione** o **eliminazione**. È progettato per aiutare amministratori e utenti a **ridurre sprechi di risorse** e **ottimizzare i costi** in ambienti cloud condivisi.

## Funzionalità principali

### 🔎 Rilevamento automatico delle VM inattive

* Le istanze vengono analizzate per determinare **periodi di inattività prolungata**, utilizzando lo stato corrente e i dati di attività.
* Le macchine in stato `SHUTOFF` da un tempo superiore a una soglia predefinita sono considerate "idle".

### 💸 Stima accurata dei costi

* Il plugin calcola il **costo effettivo** di ciascuna VM, tenendo conto:

  * del tempo reale in cui è stata attiva (uptime calcolato tramite eventi `START` e `STOP`);
  * delle risorse allocate: vCPU, RAM (in GB), e disco (in GB).
* Il disco viene considerato come sempre attivo a partire dalla creazione della VM (`created_at`), mentre CPU e RAM solo nei periodi effettivamente in esecuzione.

### 📊 Dashboard con dati aggiornati in tempo reale

* Visualizzazione centralizzata di:

  * Tutte le VM attive;
  * Le VM identificate come inattive;
  * Uptime reale, tempo di inattività, e costo stimato per ogni istanza.
* I dati si aggiornano dinamicamente senza bisogno di ricaricare la pagina.

### 🛠️ Azioni rapide: "Riattiva" e "Elimina"

* Interfaccia web interattiva con conferme utente per:

  * **Riavviare una VM** (`START`) direttamente dalla tabella delle inattive;
  * **Eliminare una VM** (`DELETE`) per liberare risorse e fermare i costi.
* Le azioni vengono eseguite via `fetch()` con aggiornamento automatico delle tabelle.

---

## Perché usare Cloudcost Idle?

In un'infrastruttura cloud come OpenStack, è facile dimenticare VM lasciate accese inutilmente o inattive per giorni. Questo plugin aiuta a:

* **Identificare gli sprechi**: trova VM inutilizzate o dimenticate.
* **Ottimizzare i costi**: calcola con precisione quanto ogni VM sta realmente costando.
* **Prendere decisioni rapide**: fornisce azioni immediate per riattivare o eliminare istanze.
* **Aumentare la consapevolezza degli utenti**: visualizzazione chiara e aggiornata dei costi e utilizzi.

---

## Architettura del plugin

* **Flask** come backend web.
* **OpenStack SDK** per interrogare i dati delle VM e gli eventi.
* **JavaScript (fetch + DOM API)** per interazione asincrona e aggiornamenti live.
* **Template HTML** separati per VM attive (`index.html`) e inattive (`idle_modal.html`).
* **Moduli Python**:

  * `dashboard.py`: logica principale e routing Flask.
  * `cost_estimator.py`: calcolo costi e uptime VM.
  * `idle_detector.py`: rilevamento VM inattive.

---

## Requisiti

* Python 3.8+
* OpenStack SDK (`openstacksdk`)
* Flask

Installa le dipendenze con:

```bash
source venv/bin/activate
pip install requirements.txt
```

---

## Avvio del server

Per avviare il server Flask:

```bash
python3 dashboard.py
```

Poi visita `http://localhost:5000` nel browser.

---

## File principali

| File                        | Descrizione                                 |
| --------------------------- | ------------------------------------------- |
| `dashboard.py`              | Server Flask e routing principale           |
| `cost_estimator.py`         | Funzioni per calcolo costi e uptime         |
| `idle_detector.py`          | Logica per trovare VM inattive              |
| `templates/index.html`      | Dashboard principale                        |
| `templates/idle_modal.html` | Vista delle VM inattive                     |
| `modals.html`               | Finestre modali per  "Riattiva" e "Elimina" |
| `static/actions.js`         | Script JS per azioni "Riattiva" e "Elimina" |
---

## Personalizzazione

* Puoi modificare le **tariffe per vCPU, RAM e Disco** nel file `cost_estimator.py`.
* La soglia di inattività (es. 30 min) può essere configurata nel modulo `idle_detector.py`.

---

