import psutil  # Import system and process utilities
import time  # Import time module for time-related functions
import threading  # Import threading for concurrent execution
from flask import Flask, request, jsonify, render_template, send_file  # Import Flask components
from collections import deque  # Import deque for efficient queue operations
import random  # Import random for generating random numbers

app = Flask(__name__)  # Initialize Flask application

# File to store traffic logs
LOG_FILE = "traffic_logs.txt"  # Define log file name

# Global variables to store logs and metrics
traffic_logs = []  # Stores HTTP logs for display
throughput = deque(maxlen=60)  # Bytes sent/received per second
latency = deque(maxlen=60)  # Simulated latency data
cpu_usage = deque(maxlen=60)  # CPU usage over time
memory_usage = deque(maxlen=60)  # Memory usage over time
high_traffic_alert = False  # Flag for high traffic alert


def log_network_traffic():
    """Continuously log incoming and outgoing traffic system-wide."""
    global high_traffic_alert  # Access global variable

    while True:  # Infinite loop for continuous logging
        net_io = psutil.net_io_counters()  # Get network I/O statistics
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
        log_entry = (  # Create log entry string
            f"{timestamp} - Bytes Sent: {net_io.bytes_sent}, "
            f"Bytes Received: {net_io.bytes_recv}\n"
        )

        # Write to log file
        with open(LOG_FILE, "a") as f:  # Open log file in append mode
            f.write(log_entry)  # Write log entry to file

        # Calculate throughput (bytes per second)
        throughput.append({  # Append current throughput data
            "timestamp": timestamp,
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
        })

        # Simulate latency data for testing (replace with real latency data if available)
        latency.append(random.uniform(10, 100))  # Random latency in milliseconds

        # Capture system resource usage
        cpu_usage.append(psutil.cpu_percent(interval=None))  # Get CPU usage percentage
        memory_usage.append(psutil.virtual_memory().percent)  # Get memory usage percentage

        # Check for high traffic (arbitrary threshold: > 1MB/sec sent or received)
        sent_rate = (throughput[-1]["bytes_sent"] - throughput[0]["bytes_sent"]) / len(throughput)  # Calculate sent rate
        recv_rate = (throughput[-1]["bytes_recv"] - throughput[0]["bytes_recv"]) / len(throughput)  # Calculate received rate
        high_traffic_alert = sent_rate > 1e6 or recv_rate > 1e6  # Set alert if traffic exceeds threshold

        time.sleep(1)  # Log every second


@app.route('/')  # Define route for home page
def index():
    """Render the home page."""
    return render_template('index.html')  # Render HTML template


@app.route('/api/traffic')  # Define route for traffic logs API
def get_traffic_logs():
    """Provide traffic logs and metrics for the frontend."""
    return jsonify({  # Return JSON response
        "traffic_logs": traffic_logs,
        "throughput": list(throughput),
        "latency": list(latency),
        "cpu_usage": list(cpu_usage),
        "memory_usage": list(memory_usage),
        "high_traffic_alert": high_traffic_alert,
    })


@app.route('/download_logs')  # Define route for downloading logs
def download_logs():
    """Download the traffic log file."""
    return send_file(LOG_FILE, as_attachment=True)  # Send log file as attachment


@app.after_request  # Define function to run after each request
def log_traffic(response):
    """Log incoming and outgoing HTTP requests to the home page."""
    log_entry = {  # Create log entry dictionary
        "ip": request.remote_addr,  # Get client IP address
        "method": request.method,  # Get HTTP method
        "path": request.path,  # Get request path
        "response_status": response.status_code,  # Get response status code
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),  # Get current timestamp
    }
    traffic_logs.append(log_entry)  # Append log entry to traffic logs

    # Limit logs to the last 100 entries for display
    if len(traffic_logs) > 100:  # Check if logs exceed limit
        traffic_logs.pop(0)  # Remove oldest log entry

    return response  # Return response


if __name__ == '__main__':  # Check if script is run directly
    # Start network traffic logging in a separate thread
    threading.Thread(target=log_network_traffic, daemon=True).start()  # Start logging thread
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run Flask app
