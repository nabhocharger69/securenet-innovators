import psutil
import time
import threading
from flask import Flask, request, jsonify, render_template, send_file
from collections import deque
import random

app = Flask(__name__)

# File to store traffic logs
LOG_FILE = "traffic_logs.txt"

# Global variables to store logs and metrics
traffic_logs = []  # Stores HTTP logs for display
throughput = deque(maxlen=60)  # Bytes sent/received per second
latency = deque(maxlen=60)  # Simulated latency data
cpu_usage = deque(maxlen=60)  # CPU usage over time
memory_usage = deque(maxlen=60)  # Memory usage over time
high_traffic_alert = False


def log_network_traffic():
    """Continuously log incoming and outgoing traffic system-wide."""
    global high_traffic_alert

    while True:
        net_io = psutil.net_io_counters()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"{timestamp} - Bytes Sent: {net_io.bytes_sent}, "
            f"Bytes Received: {net_io.bytes_recv}\n"
        )

        # Write to log file
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)

        # Calculate throughput (bytes per second)
        throughput.append({
            "timestamp": timestamp,
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
        })

        # Simulate latency data for testing (replace with real latency data if available)
        latency.append(random.uniform(10, 100))  # Random latency in milliseconds

        # Capture system resource usage
        cpu_usage.append(psutil.cpu_percent(interval=None))
        memory_usage.append(psutil.virtual_memory().percent)

        # Check for high traffic (arbitrary threshold: > 1MB/sec sent or received)
        sent_rate = (throughput[-1]["bytes_sent"] - throughput[0]["bytes_sent"]) / len(throughput)
        recv_rate = (throughput[-1]["bytes_recv"] - throughput[0]["bytes_recv"]) / len(throughput)
        high_traffic_alert = sent_rate > 1e6 or recv_rate > 1e6

        time.sleep(1)  # Log every second


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/api/traffic')
def get_traffic_logs():
    """Provide traffic logs and metrics for the frontend."""
    return jsonify({
        "traffic_logs": traffic_logs,
        "throughput": list(throughput),
        "latency": list(latency),
        "cpu_usage": list(cpu_usage),
        "memory_usage": list(memory_usage),
        "high_traffic_alert": high_traffic_alert,
    })


@app.route('/download_logs')
def download_logs():
    """Download the traffic log file."""
    return send_file(LOG_FILE, as_attachment=True)


@app.after_request
def log_traffic(response):
    """Log incoming and outgoing HTTP requests to the home page."""
    log_entry = {
        "ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "response_status": response.status_code,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    traffic_logs.append(log_entry)

    # Limit logs to the last 100 entries for display
    if len(traffic_logs) > 100:
        traffic_logs.pop(0)

    return response


if __name__ == '__main__':
    # Start network traffic logging in a separate thread
    threading.Thread(target=log_network_traffic, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
