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

function configure_green_cloud_plugin {
    echo "Plugin configurato."
}

function start_green_cloud_plugin {
    echo "Creazione istanza test..."
    openstack server create \
      --image "$IMAGE_NAME" \
      --flavor "$FLAVOR_NAME" \
      --network "$NET_NAME" \
      --user-data "$PLUGIN_DIR/cloud-init/user-data.sh" \
      green-instance-1

    echo "Attesa avvio VM..."
    sleep 30

    echo "Avvio servizio Green Cloud..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable green-cloud.service
    sudo systemctl restart green-cloud.service
}

function copy_service_file {
    sudo cp $PLUGIN_DIR/systemd/green-cloud.service $SYSTEMD_DIR/
}

if is_service_enabled green-cloud; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "Nessun pacchetto aggiuntivo richiesto."

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installazione dipendenze Flask..."
        install_flask_dependencies
        copy_service_file

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configurazione plugin Green Cloud..."
        configure_green_cloud_plugin

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Esecuzione Green Cloud Plugin..."
        start_green_cloud_plugin
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Arresto servizio Green Cloud..."
        sudo systemctl stop green-cloud.service || { echo "Errore nell'arresto"; exit 1; }
    fi

    if [[ "$1" == "clean" ]]; then
        sudo rm -f $SYSTEMD_DIR/green-cloud.service
    fi
fi
