#!/bin/bash
source /opt/stack/devstack/openrc admin admin
/opt/stack/snapshot-scheduler/venv/bin/python /opt/stack/snapshot-scheduler/app/scheduler.py

chmod +x /opt/stack/snapshot-scheduler/scheduler/start-scheduler.sh
