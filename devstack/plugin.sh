#!/bin/bash

# Source common DevStack functions
source $TOP_DIR/functions
source $TOP_DIR/lib/nova

# Plugin settings
PLUGIN_NAME=green-cloud
SYSTEMD_DIR=/etc/systemd/system

function install_flask_dependencies {
    sudo apt-get update
    sudo apt-get install -y python3-pip
    sudo pip3 install -r $DEST/green-cloud-plugin/webapp/requirements.txt
}

function configure_green_cloud_plugin {
    echo "Green Cloud Plugin configured"
}

function start_green_cloud_plugin {
    echo "Starting Green Cloud Plugin web app..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable green-cloud.service
    sudo systemctl restart green-cloud.service
}

function copy_service_file {
    sudo cp $DEST/green-cloud-plugin/green-cloud.service $SYSTEMD_DIR/
}

function create_demo_instance {
    echo "Creating demo instance..."
    source $TOP_DIR/openrc admin admin
    openstack server create --flavor m1.small --image cirros --network private demo-instance || echo "Demo instance already exists or failed"
}

if is_service_enabled $PLUGIN_NAME; then
    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "No pre-install actions for $PLUGIN_NAME"

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Flask dependencies"
        install_flask_dependencies
        copy_service_file

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring $PLUGIN_NAME"
        configure_green_cloud_plugin

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        create_demo_instance
        start_green_cloud_plugin
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Stopping Green Cloud Plugin service"
        sudo systemctl stop green-cloud.service
    fi

    if [[ "$1" == "clean" ]]; then
        sudo rm "$SYSTEMD_DIR/green-cloud.service"
    fi
fi

# settings

enable_service green-cloud
