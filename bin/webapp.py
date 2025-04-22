from flask import Flask, render_template
from app.cost_estimator import get_costs
from app.idle_detector import get_idle_instances

app = Flask(__name__)

@app.route("/")
def index():
    costs = get_costs()
    idle = get_idle_instances()
    return render_template("index.html", costs=costs, idle=idle)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
