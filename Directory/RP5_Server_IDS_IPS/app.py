import psutil
import time
import threading
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)

# File to store traffic logs
LOG_FILE = "traffic_logs.txt"

# Global variable to store logs for displaying on the home page
traffic_logs = []


def log_network_traffic():
    """Continuously log incoming and outgoing traffic system-wide."""
    with open(LOG_FILE, "a") as f:
        while True:
            # Get network traffic stats
            net_io = psutil.net_io_counters()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = (
                f"{timestamp} - Bytes Sent: {net_io.bytes_sent}, "
                f"Bytes Received: {net_io.bytes_recv}\n"
            )
            f.write(log_entry)
            f.flush()  # Ensure immediate write to file
            time.sleep(1)  # Log every second


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/api/traffic')
def get_traffic_logs():
    """Provide traffic logs for the frontend."""
    return jsonify({"traffic_logs": traffic_logs})


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
    app.run(host='0.0.0.0', port=5000)
