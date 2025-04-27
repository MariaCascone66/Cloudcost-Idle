import os
from flask import Flask, render_template, redirect, url_for
from cost_estimator import estimate_instance_cost, create_connection
from idle_detector import detect_idle_instances

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
        costs.append(cost_info)
    return render_template('index.html', costs=costs)

@app.route('/idle')
def idle():
    idle_vms = detect_idle_instances()
    return render_template('idle_modal.html', idle_vms=idle_vms)

@app.route('/delete_vm/<instance_id>')
def delete_vm(instance_id):
    conn = create_connection()
    conn.compute.delete_server(instance_id)
    return redirect(url_for('idle'))

@app.route('/download_costs')
def download_costs():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    costs = []
    for i in instances:
        cost_info = estimate_instance_cost(i)
        cost_info["created_at"] = getattr(i, "created_at", "N/A").replace('T', ' ').replace('Z', '')
        cost_info["status"] = i.status
        costs.append(cost_info)
    
    csv_file_path = export_costs_to_csv(costs)
    return send_file(csv_file_path, as_attachment=True)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
