#!/bin/bash

# Funzione chiamata da stack.sh per abilitare il plugin
function install_snapshot_scheduler {
    echo "Installing Snapshot Scheduler..."
    sudo cp $DEST/snapshot_scheduler/snapshot_scheduler.conf /etc/
    sudo pip install -r $DEST/snapshot_scheduler/requirements.txt
}

function configure_snapshot_scheduler {
    echo "Configuring Snapshot Scheduler..."
    
    # Assicurati che l'ambiente di OpenStack sia caricato (se non è già fatto)
    if [ -f $DEST/devstack/openrc ]; then
        source $DEST/devstack/openrc
    fi

    # Qui non è necessario reimpostare le variabili, in quanto sono già presenti in openrc
    echo "Snapshot Scheduler configured with OpenStack environment from openrc."

    # Se necessario, puoi aggiungere altre configurazioni specifiche per il tuo plugin, come i parametri di retention
    #export SNAPSHOT_RETENTION_DAYS=7
    #export SNAPSHOT_INTERVAL_MINUTES=30

    #echo "Configuration complete. Retention: $SNAPSHOT_RETENTION_DAYS days, Interval: $SNAPSHOT_INTERVAL_MINUTES minutes"
}


function start_snapshot_scheduler {
    echo "Starting Snapshot Scheduler..."
    sudo nohup python3 $DEST/snapshot_scheduler/scheduler.py > /var/log/snapshot_scheduler.log 2>&1 &
}

# Registriamo il servizio
if [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_snapshot_scheduler
elif [[ "$1" == "stack" && "$2" == "configure" ]]; then
    configure_snapshot_scheduler
elif [[ "$1" == "stack" && "$2" == "start" ]]; then
    start_snapshot_scheduler
fi
