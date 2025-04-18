# CloudWatcher Plugin

**CloudWatcher** è un plugin per monitorare e gestire l'utilizzo delle risorse in OpenStack. Il plugin fornisce funzionalità per visualizzare le informazioni sulle VM, monitorare lo stato delle risorse (CPU, RAM, disco) e assegnare un "stato meteo" in base al carico delle risorse. Include anche una dashboard per visualizzare le quote del progetto e la possibilità di creare nuove VM tramite una semplice interfaccia web.

## Funzionalità

1. **Dashboard VM**:
   - Visualizza una lista di tutte le VM con lo stato meteo attuale (☀️, 🌤️, 🌩️) in base al carico della CPU.
   - Visualizza le informazioni relative alle risorse (CPU, RAM, Disco) delle VM.
   
2. **Tagging meteo delle VM**:
   - Ogni VM è etichettata con uno stato meteo in base all'utilizzo delle risorse (CPU, RAM, disco).
   - Viene generato un carico simulato (casuale) per testare la funzionalità senza la necessità di un carico reale.

3. **Creazione di nuove VM**:
   - Nuove VM possono essere create tramite una semplice interfaccia web, con la possibilità di scegliere l'immagine, il flavor e la rete.
   - I parametri richiesti includono nome, immagine, flavor, e ID della rete.

4. **Quota del progetto**:
   - Visualizza le quote di CPU e RAM per ogni progetto, mostrando l'utilizzo corrente rispetto al limite assegnato.

5. **Modalità simulata**:
   - È possibile abilitare la modalità simulata per generare valori casuali di utilizzo delle risorse (CPU, RAM, Disco), utile per i test.

## Prerequisiti

- **Python 3.6+**
- **OpenStack SDK** (installabile tramite `pip install openstacksdk`).
- **Flask** per la dashboard web.
- **Waitress** per servire l'app Flask.
- Un'istanza di **OpenStack** con credenziali di accesso configurate tramite variabili d'ambiente o nel file di configurazione.

## Installazione

1. **Clonare il repository**:

   ```bash
   git clone https://your-repository-url
   cd cloudwatcher
   ```

2. **Installare le dipendenze**:

   Crea un ambiente virtuale (opzionale ma consigliato):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configurare le variabili d'ambiente**:

   Assicurati di avere le seguenti variabili d'ambiente configurate:

   - `OS_AUTH_URL`
   - `OS_USERNAME`
   - `OS_PASSWORD`
   - `OS_PROJECT_NAME`
   - `OS_USER_DOMAIN_ID`
   - `OS_PROJECT_DOMAIN_ID`
   - `OS_REGION_NAME` (opzionale, default: `RegionOne`)


4. **Avviare il server**:

   ```bash
   python3 cloudwatcher/bin/quota_dashboard.py
   ```

   Questo avvierà il server web Flask sulla porta 5001.

5. **Accedere alla dashboard**:

   Vai nel tuo browser e accedi a `http://localhost:5001` per visualizzare la dashboard delle VM e delle quote.

## Struttura del Progetto

```plaintext
cloudwatcher/
│
├── bin/
│   ├── quota_dashboard.py      # Server Flask per la dashboard
│   ├── weather_tagger.py       # Script per il tagging meteo delle VM
│   └── auth.py                 # Autenticazione con OpenStack
│
├── templates/
│   ├── index.html              # Template della dashboard principale
│   └── create_vm.html          # Template per la creazione delle VM
│
├── requirements.txt            # Dipendenze del progetto
└── README.md                   # Documentazione
```

## Come Funziona

### Dashboard

La dashboard mostra le VM in esecuzione con il loro stato meteo (basato sull'uso della CPU). Le VM sono etichettate come "Sunny", "Cloudy" o "Stormy" in base all'utilizzo della CPU. Puoi anche visualizzare le quote del progetto, che mostrano l'utilizzo corrente rispetto alle risorse allocate.

### Creazione di VM

Puoi creare una nuova VM tramite la sezione "Create VM" della dashboard. I parametri richiesti includono:

- **Nome della VM**
- **ID dell'immagine**
- **ID del flavor**
- **ID della rete**

Dopo aver inviato il modulo, la VM verrà creata in OpenStack e la pagina verrà aggiornata con la nuova VM.

### Carico Simulato

Se abilitato, il carico simulato genera valori casuali per CPU, RAM e Disco. Questi valori vengono utilizzati per calcolare lo stato meteo delle VM senza la necessità di un carico reale. I valori simulati sono visibili nel metadata della VM.

## Esempio di uso

1. Per creare una nuova VM, clicca su "Create VM" nella dashboard.
2. Compila il modulo con i dati richiesti (nome, immagine, flavor, network).
3. La VM verrà creata e mostrata nella lista delle VM nella dashboard.
4. Ogni 60 secondi, il tagger aggiorna automaticamente lo stato meteo delle VM.

