#!/bin/bash

DEST=${DEST:-/opt/stack}
PLUGIN_DIR=$DEST/green-cloud-plugin
SYSTEMD_DIR=/etc/systemd/system

source $PLUGIN_DIR/devstack/settings

function install_flask_dependencies {
    sudo apt update
    sudo apt install -y python3-pip
    pip install -r $PLUGIN_DIR/webapp/requirements.txt
}

function configure_snap_stack_plugin {
    echo "Plugin configurato."
}

function start_snap_stack_plugin {
    echo "Creazione istanza test..."
    openstack server create \
      --image "$IMAGE_NAME" \
      --flavor "$FLAVOR_NAME" \
      --network "$NET_NAME" \
      --user-data "$PLUGIN_DIR/cloud-init/user-data.sh" \
      green-instance-1

    echo "Attesa avvio VM..."
    sleep 30

    echo "Avvio servizio Snap Stack..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable snap-stack.service
    sudo systemctl restart snap-stack.service
}

function copy_service_file {
    sudo cp $PLUGIN_DIR/systemd/snap-stack.service $SYSTEMD_DIR/
}

if is_service_enabled snap-stack; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "Nessun pacchetto aggiuntivo richiesto."

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installazione dipendenze Flask..."
        install_flask_dependencies
        copy_service_file

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configurazione plugin Snap Stack..."
        configure_snap_stack_plugin

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Esecuzione Snap Stack Plugin..."
        start_snap_stack_plugin
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Arresto servizio Snap Stack..."
        sudo systemctl stop snap-stack.service || { echo "Errore nell'arresto"; exit 1; }
    fi

    if [[ "$1" == "clean" ]]; then
        sudo rm -f $SYSTEMD_DIR/snap-stack.service
    fi
fi
