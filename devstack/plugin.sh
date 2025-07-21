#!/bin/bash
# === Load plugin settings ===
source ${BASH_SOURCE%/*}/settings

function install_flask_dependencies() {
    echo "Installing Flask and dependencies..."
    if [[ ! -d "$APP_DIR/venv" ]]; then
        python3 -m venv "$APP_DIR/venv"
    fi
    source "$APP_DIR/venv/bin/activate"
    pip install -r "$APP_DIR/requirements.txt" || exit 1
    deactivate
}

function copy_service_file() {
    echo "Copying service file to systemd directory..."
    sudo cp "$SERVICE_DIR/cloudcost_idle.service" "$SYSTEMD_DIR"
    sudo systemctl daemon-reload
    sudo systemctl enable cloudcost_idle.service
}

function start_plugin() {
    echo "Starting plugin..."
    sudo systemctl start cloudcost_idle.service
}

function stop_plugin() {
    echo "Stopping plugin..."
    sudo systemctl stop cloudcost_idle.service
}

function install_nova_filter() {
    echo "Installing IdleVMFilter into Nova filters..."
    sudo cp "$APP_DIR/nova_filter/idle_vm_filter.py" /opt/stack/nova/nova/scheduler/filters/
}

function configure_nova_filter() {
    echo "Enabling IdleVMFilter in nova.conf..."
    iniset /etc/nova/nova.conf DEFAULT scheduler_available_filters nova.scheduler.filters.all_filters
    iniset /etc/nova/nova.conf DEFAULT scheduler_default_filters RetryFilter,AvailabilityZoneFilter,IdleVMFilter
}

function restart_nova_scheduler() {
    echo "Restarting nova scheduler service..."
    sudo systemctl restart devstack@n-sch.service || sudo systemctl restart nova-scheduler
}

if is_service_enabled cloudcost_idle; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        install_flask_dependencies
        copy_service_file
        install_nova_filter
        configure_nova_filter
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        start_plugin
        restart_nova_scheduler
    elif [[ "$1" == "unstack" ]]; then
        stop_plugin
    fi
fi
