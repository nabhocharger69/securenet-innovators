from flask import Flask, request, jsonify, render_template
import time
import threading

app = Flask(__name__)

# Global variables for traffic data
traffic_data = {
    "total_requests": 0,
    "endpoint_stats": {},
    "response_times": [],
    "detailed_logs": [],
}

lock = threading.Lock()


@app.before_request
def before_request():
    """Log the start time of the request."""
    request.start_time = time.time()


@app.after_request
def after_request(response):
    """Log request details and calculate response time."""
    response_time = time.time() - request.start_time
    with lock:
        traffic_data["total_requests"] += 1
        traffic_data["response_times"].append(response_time)
        endpoint = request.endpoint
        method = request.method
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Update endpoint stats
        if endpoint in traffic_data["endpoint_stats"]:
            traffic_data["endpoint_stats"][endpoint] += 1
        else:
            traffic_data["endpoint_stats"][endpoint] = 1

        # Log detailed request
        traffic_data["detailed_logs"].append({
            "timestamp": timestamp,
            "endpoint": endpoint,
            "method": method,
            "response_time": f"{response_time:.2f} seconds"
        })

        # Limit logs to the last 50 entries
        if len(traffic_data["detailed_logs"]) > 50:
            traffic_data["detailed_logs"].pop(0)
    return response


@app.route("/")
def home():
    """Serve the analytics page."""
    return render_template("index.html")


@app.route("/analytics")
def analytics():
    """API to fetch traffic analytics."""
    with lock:
        avg_response_time = (
            sum(traffic_data["response_times"]) / len(traffic_data["response_times"])
            if traffic_data["response_times"]
            else 0
        )
        return jsonify({
            "total_requests": traffic_data["total_requests"],
            "average_response_time": f"{avg_response_time:.2f} seconds",
            "endpoint_stats": traffic_data["endpoint_stats"],
            "detailed_logs": traffic_data["detailed_logs"],
        })


if __name__ == "__main__":
    app.run(debug=True)
