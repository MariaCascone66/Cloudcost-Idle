#!/bin/bash

# Funzione per la creazione e gestione del virtual environment
function install_flask_dependencies {
    echo "Installing Flask and dependencies..."

    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR" || { echo "Failed to create virtual environment"; exit 1; }
    fi

    source "$VENV_DIR/bin/activate"

    if [[ -f "$CLOUDWATCHER_DIR/requirements.txt" ]]; then
        pip install --upgrade pip
        pip install -r "$CLOUDWATCHER_DIR/requirements.txt" || { echo "Failed to install dependencies"; exit 1; }
    else
        echo "requirements.txt not found!"
        exit 1
    fi

    echo "Dependencies installed successfully"
    deactivate
}

# Funzione per copiare i file systemd
function copy_service_file {
    echo "Copying systemd service files..."
    sudo cp "$CLOUDWATCHER_DIR/systemd/cloudwatcher_dashboard.service" "$SYSTEMD_DIR/"
    sudo cp "$CLOUDWATCHER_DIR/systemd/cloudwatcher_tagger.service" "$SYSTEMD_DIR/"
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
}

# Funzione per avviare i servizi
function start_cloudwatcher_plugin {
    echo "Starting CloudWatcher services..."
    sudo systemctl start cloudwatcher_dashboard.service || { echo "Failed to start dashboard"; exit 1; }
    sudo systemctl start cloudwatcher_tagger.service || { echo "Failed to start tagger"; exit 1; }
}

# Funzione per fermare i servizi
function stop_cloudwatcher_plugin {
    echo "Stopping CloudWatcher services..."
    sudo systemctl stop cloudwatcher_dashboard.service
    sudo systemctl stop cloudwatcher_tagger.service
}

# Pulizia dei file systemd
function clean_cloudwatcher_plugin {
    echo "Cleaning CloudWatcher service files..."
    sudo rm -f "$SYSTEMD_DIR/cloudwatcher_dashboard.service"
    sudo rm -f "$SYSTEMD_DIR/cloudwatcher_tagger.service"
}

# Funzione per configurare i ruoli OpenStack
function configure_cloudwatcher_roles {
    echo "Configuring OpenStack roles for CloudWatcher..."

    source /opt/stack/devstack/openrc admin admin

    if ! openstack role assignment list --user admin --system all --names | grep -q "admin"; then
        echo "Assegnazione ruolo admin all'utente admin (system scope)..."
        openstack role add --user admin --system all --role admin
    else
        echo "L'utente admin ha già il ruolo admin a livello di sistema."
    fi
}

# Inizio logica plugin
if is_service_enabled cloudwatcher; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "CloudWatcher: Nessun pacchetto da installare"

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "CloudWatcher: Installing dependencies"
        install_flask_dependencies
        copy_service_file

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "CloudWatcher: Configurazione ruoli OpenStack"
        configure_cloudwatcher_roles

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "CloudWatcher: Starting service"
        start_cloudwatcher_plugin
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "CloudWatcher: Stopping service"
        stop_cloudwatcher_plugin
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "CloudWatcher: Cleaning service"
        clean_cloudwatcher_plugin
    fi
fi
