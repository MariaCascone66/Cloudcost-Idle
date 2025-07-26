# CloudCost Idle Plugin

## Overview

CloudCost Idle è un plugin integrabile in DevStack per monitorare il costo delle VM in esecuzione su OpenStack e rilevare quelle inattive (idle). Fornisce una dashboard web con aggiornamento dinamico dei costi e pulsanti di gestione (elimina/riattiva) delle VM.

La rilevazione delle VM idle avviene tramite un servizio Flask che analizza le metriche delle VM (inclusi log console e diagnostica, se abilitato).

## Struttura del progetto

```
cloudcost-idle/
├── dashboard.py              # App principale Flask con le rotte
├── idle_detector.py          # Rilevazione delle VM inattive
├── cost_estimator.py         # Calcolo costi VM
├── pricing.yaml              # Tariffe orarie per vCPU, RAM, Disco
├── plugin.sh                # Script di hook per DevStack
├── settings                 # Configurazione del plugin DevStack
├── static/
│   └── actions.js            # Script JS lato client (modali, refresh, ecc.)
├── templates/
    ├── index.html            # Dashboard principale
    ├── idle_modal.html       # Modale con VM inattive
    └── modals.html           # Modali generiche (delete/reactivate)
```

## Requisiti

* OpenStack (Nova, Glance, ecc.) con autenticazione funzionante
* DevStack funzionante
* Python >= 3.8
* Flask
* openstacksdk
* systemd (per eseguire il servizio come demone)

## Installazione con DevStack

1. Posizionare il progetto in `~/devstack/cloudcost-idle/`
2. Nel file `local.conf`, aggiungere:

   ```ini
   [[local|localrc]]
   enable_plugin cloudcost-idle /percorso/assoluto/cloudcost-idle
   ```
3. Eseguire DevStack:

   ```bash
   ./stack.sh
   ```

   Il plugin avvierà il servizio Flask su porta `8081` e creerà un servizio systemd `cloudcost-idle.service`.

## Avvio manuale del servizio

In alternativa a DevStack:

```bash
source openrc admin admin
python3 dashboard.py
```

## Variabili d'ambiente richieste

Il servizio Flask usa le stesse variabili d'ambiente di OpenStack:

* `OS_AUTH_URL`
* `OS_PROJECT_NAME`
* `OS_USERNAME`
* `OS_PASSWORD`
* `OS_USER_DOMAIN_NAME`
* `OS_PROJECT_DOMAIN_NAME`
* `OS_REGION_NAME`

## File di tariffe (`pricing.yaml`)

```yaml
vcpu_hour: 0.05
ram_gb_hour: 0.01
disk_gb_hour: 0.005
```

Valori personalizzabili per il calcolo dei costi.

## Funzionalità principali

### Dashboard Web ([http://localhost:8081](http://localhost:8081))

* Mostra tutte le VM con costi aggiornati
* Aggiorna periodicamente costi e uptime
* Pulsanti:

  * ✅ **Riattiva**: avvia una VM spenta
  * ❌ **Elimina**: elimina una VM
  * ⌛ **Aggiorna VM**: forza reload
  * ⚡ **Check Idle**: mostra VM inattive

### Endpoint API

* `/api/idle_vms`: restituisce la lista JSON delle VM inattive
* `/check_vm_status/<instance_id>`: stato di una singola VM
* `/check_vm_exists/<instance_id>`: verifica esistenza VM

## Systemd (opzionale)

Il plugin installa automaticamente un servizio systemd:

```ini
[Unit]
Description=CloudCost Idle Flask App
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/stack/cloudcost-idle/dashboard.py
WorkingDirectory=/opt/stack/cloudcost-idle
EnvironmentFile=-/opt/stack/cloudcost-idle/.env
Restart=always
User=stack

[Install]
WantedBy=multi-user.target
```

### Comandi utili

```bash
sudo systemctl restart cloudcost-idle
sudo systemctl status cloudcost-idle
```

## Note

* Alcune funzionalità (es. log console, diagnostica Nova) richiedono privilegi admin.
* Il plugin è compatibile con deployment all'interno di DevStack, ma può anche essere eseguito standalone.

## Autori

Progetto sviluppato per integrazione OpenStack DevStack 2025.

---
