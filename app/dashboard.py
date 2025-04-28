import os
from flask import Flask, render_template, redirect, url_for, request
from cost_estimator import estimate_instance_cost, create_connection
from idle_detector import detect_idle_instances
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '../templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

@app.route('/')
def index():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    costs = []
    for i in instances:
        cost_info = estimate_instance_cost(i)
        cost_info["created_at"] = getattr(i, "created_at", "N/A").replace('T', ' ').replace('Z', '')
        cost_info["status"] = i.status
        cost_info["reactivation_date"] = getattr(i, "reactivation_date", None)  # New field for reactivation date
        costs.append(cost_info)
    return render_template('index.html', costs=costs)

@app.route('/idle')
def idle():
    idle_vms = detect_idle_instances()
    return render_template('idle_modal.html', idle_vms=idle_vms)

@app.route('/reactivate_vm/<instance_id>', methods=['GET', 'POST'])
def reactivate_vm(instance_id):
    if request.method == 'POST':
        conn = create_connection()
        instance = conn.compute.get_server(instance_id)
        
        # Reactivate the instance on OpenStack
        conn.compute.start_server(instance_id)
        
        # Record the reactivation date
        reactivation_date = datetime.now().isoformat()
        instance.metadata['reactivation_date'] = reactivation_date
        conn.compute.set_server_metadata(instance_id, metadata=instance.metadata)

        return redirect(url_for('index'))

    return render_template('reactivate_modal.html', instance_id=instance_id)

@app.route('/delete_vm/<instance_id>', methods=['GET', 'POST'])
def delete_vm(instance_id):
    if request.method == 'POST':
        conn = create_connection()
        instance = conn.compute.get_server(instance_id)
        
        # Check if the instance has connected volumes or related resources
        related_resources = conn.compute.volume_attachments(instance_id)
        if related_resources:
            return render_template('confirm_delete_with_related.html', instance_name=instance.name, instance_id=instance_id)
        
        # Delete the instance
        conn.compute.delete_server(instance_id)
        return redirect(url_for('index'))
    
    return render_template('delete_modal.html', instance_id=instance_id)

@app.route('/confirm_delete_related/<instance_id>', methods=['POST'])
def confirm_delete_related(instance_id):
    conn = create_connection()
    instance = conn.compute.get_server(instance_id)
    
    # Delete the instance and any related resources (volumes, etc.)
    conn.compute.delete_server(instance_id)
    
    # Optionally delete related volumes or other resources
    related_volumes = conn.compute.volume_attachments(instance_id)
    for volume in related_volumes:
        conn.compute.delete_volume(volume['id'])

    return redirect(url_for('index'))

@app.route('/download_costs')
def download_costs():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    costs = []
    for i in instances:
        cost_info = estimate_instance_cost(i)
        cost_info["created_at"] = getattr(i, "created_at", "N/A").replace('T', ' ').replace('Z', '')
        cost_info["status"] = i.status
        cost_info["reactivation_date"] = getattr(i, "reactivation_date", None)
        costs.append(cost_info)
    
    csv_file_path = export_costs_to_csv(costs)
    return send_file(csv_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
