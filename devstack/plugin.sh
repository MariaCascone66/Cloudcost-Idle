#!/bin/bash

function install_flask_dependencies {
    echo "Installing Flask and OpenStack SDK..."
    pip_install -r $CLOUDWATCHER_DIR/requirements.txt
}

function copy_service_file {
    echo "Copying systemd service file..."
    sudo cp $CLOUDWATCHER_DIR/systemd/cloudwatcher.service $SYSTEMD_DIR/cloudwatcher.service
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
}

function configure_cloudwatcher_plugin {
    echo "Configuring CloudWatcher plugin..."
    # Add extra config here if needed
}

function start_cloudwatcher_plugin {
    echo "Starting CloudWatcher service..."
    sudo systemctl start cloudwatcher.service || { echo "Failed to start service"; exit 1; }
}

function stop_cloudwatcher_plugin {
    echo "Stopping CloudWatcher service..."
    sudo systemctl stop cloudwatcher.service || { echo "Failed to stop service"; exit 1; }
}

function clean_cloudwatcher_plugin {
    echo "Cleaning CloudWatcher files..."
    sudo rm -f $SYSTEMD_DIR/cloudwatcher.service
}

if is_service_enabled cloudwatcher; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "CloudWatcher: No pre-install actions."

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "CloudWatcher: Installing dependencies"
        install_flask_dependencies
        copy_service_file

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "CloudWatcher: Post configuration"
        configure_cloudwatcher_plugin

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
