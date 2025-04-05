#!/bin/bash

# Called during DevStack setup (stack.sh)
function install_auto_snapshot {
    echo "Installing snapshot-scheduler plugin"
    pip_install_gr snapshotlib
}

function configure_auto_snapshot {
    echo "Configuring snapshot-scheduler  plugin"
    # Crea un cron job semplice per esempio
    (crontab -l 2>/dev/null; echo "*/$((AUTO_SNAPSHOT_INTERVAL / 60)) * * * * /usr/bin/python3 /opt/stack/snapshot-scheduler /snapshot_agent.py") | crontab -
}

function start_auto_snapshot {
    echo "snapshot-scheduler  will run in background via cron"
}

# Main plugin logic
if [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_auto_snapshot
elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    configure_auto_snapshot
elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
    start_auto_snapshot
fi
