#!/usr/bin/env bash
# devstack/plugin.sh – hook DevStack life‑cycle

function install_cloudcost {
    echo "Installing requirements in venv"
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    pip install -U pip
    pip install -r $CLOUDCOST_DIR/requirements.txt
    deactivate
}

function configure_cloudcost {
    echo "Installing systemd services"
    sudo install -m644 $CLOUDCOST_DIR/systemd/*.service $SYSTEMD_DIR/
    sudo systemctl daemon-reload
}

function start_cloudcost {
    echo "Starting CloudCost‑Idle services"
    sudo systemctl enable --now cloudcost_collector.service
    sudo systemctl enable --now cloudcost_dashboard.service
}

function stop_cloudcost {
    sudo systemctl disable --now cloudcost_collector.service
    sudo systemctl disable --now cloudcost_dashboard.service
}

# ── DevStack entry points ───────────────────────────────────────────
if [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_cloudcost
    configure_cloudcost
elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
    start_cloudcost
fi

if [[ "$1" == "unstack" ]]; then
    stop_cloudcost
fi
