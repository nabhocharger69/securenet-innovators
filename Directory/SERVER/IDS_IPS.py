import tkinter as tk  # Import tkinter for GUI
import requests  # Import requests for HTTP requests
import threading  # Import threading for concurrent execution
import time  # Import time for time-related functions
from collections import deque  # Import deque for efficient queue operations


class IDSApp:
    def __init__(self, root, server_url):
        self.root = root  # Store the root window
        self.server_url = server_url  # Store the server URL
        self.root.title("Interactive IDS/IPS Logs")  # Set window title

        # Create a text box to display logs
        self.log_display = tk.Text(root, height=20, width=100)  # Initialize log display
        self.log_display.pack(pady=10)  # Add padding

        # Labels for displaying metrics
        self.throughput_label = tk.Label(root, text="Throughput (Bytes Sent/Received): N/A")  # Throughput label
        self.throughput_label.pack(pady=5)  # Add padding

        self.latency_label = tk.Label(root, text="Latency (ms): N/A")  # Latency label
        self.latency_label.pack(pady=5)  # Add padding

        self.cpu_usage_label = tk.Label(root, text="CPU Usage (%): N/A")  # CPU usage label
        self.cpu_usage_label.pack(pady=5)  # Add padding

        self.memory_usage_label = tk.Label(root, text="Memory Usage (%): N/A")  # Memory usage label
        self.memory_usage_label.pack(pady=5)  # Add padding

        self.high_traffic_alert_label = tk.Label(root, text="High Traffic Alert: N/A")  # High traffic alert label
        self.high_traffic_alert_label.pack(pady=5)  # Add padding

        # Button to toggle traffic monitoring
        self.toggle_button = tk.Button(root, text="Pause Monitoring", command=self.toggle_monitoring)  # Toggle button
        self.toggle_button.pack(pady=5)  # Add padding

        # Internal variables
        self.running = True  # Flag to control the main loop
        self.monitoring = True  # Flag to control monitoring state
        self.traffic_data = []  # Stores traffic data with high traffic alerts
        self.request_timestamps = deque(maxlen=100)  # Timestamps to detect bursts

        # Start the monitoring in a separate thread
        self.monitoring_thread = threading.Thread(target=self.update_logs, daemon=True)  # Create monitoring thread
        self.monitoring_thread.start()  # Start the thread

    def fetch_traffic_data(self):
        """Fetch traffic data from the Flask server."""
        try:
            response = requests.get(f"{self.server_url}/api/traffic")  # Send GET request
            if response.status_code == 200:  # Check for successful response
                return response.json()  # Return JSON data
            else:
                return None  # Return None for unsuccessful response
        except Exception as e:
            return None  # Return None on exception

    def detect_high_traffic(self):
        """Detect high traffic bursts (50 requests in 0.5 seconds)."""
        current_time = time.time()  # Get current time
        self.request_timestamps.append(current_time)  # Add current timestamp

        # Remove old timestamps (older than 0.5 seconds)
        while self.request_timestamps and self.request_timestamps[0] < current_time - 0.5:  # Check for old timestamps
            self.request_timestamps.popleft()  # Remove old timestamp

        # If there are 50 requests within the last 0.5 seconds, high traffic is detected
        return len(self.request_timestamps) >= 50  # Return True if high traffic detected

    def update_logs(self):
        """Fetch and display logs and metrics every second."""
        while self.running:  # Loop while running
            if self.monitoring:  # Check if monitoring is active
                data = self.fetch_traffic_data()  # Fetch traffic data

                if data:  # If data is available
                    traffic_logs = data["traffic_logs"]  # Extract traffic logs
                    throughput = data["throughput"]  # Extract throughput
                    latency = data["latency"]  # Extract latency
                    cpu_usage = data["cpu_usage"]  # Extract CPU usage
                    memory_usage = data["memory_usage"]  # Extract memory usage
                    high_traffic_alert = data["high_traffic_alert"]  # Extract high traffic alert

                    # Update the display for logs
                    self.log_display.delete(1.0, tk.END)  # Clear the current text
                    for log in traffic_logs:  # Iterate through logs
                        log_entry = f"{log['timestamp']} - {log['method']} {log['path']} (IP: {log['ip']}) - {log['response_status']}\n"  # Format log entry
                        self.log_display.insert(tk.END, log_entry)  # Insert log entry

                    # Update throughput, latency, CPU, memory, and alert labels
                    if throughput:  # If throughput data exists
                        self.throughput_label.config(
                            text=f"Throughput (Bytes Sent/Received): Sent: {throughput[-1]['bytes_sent']} / Received: {throughput[-1]['bytes_recv']}")  # Update label
                    if latency:  # If latency data exists
                        self.latency_label.config(text=f"Latency (ms): {latency[-1]}")  # Update label
                    if cpu_usage:  # If CPU usage data exists
                        self.cpu_usage_label.config(text=f"CPU Usage (%): {cpu_usage[-1]}")  # Update label
                    if memory_usage:  # If memory usage data exists
                        self.memory_usage_label.config(text=f"Memory Usage (%): {memory_usage[-1]}")  # Update label

                    # Detect high traffic based on burst
                    if self.detect_high_traffic():  # Check for high traffic
                        high_traffic_alert = True  # Set alert

                    self.high_traffic_alert_label.config(
                        text=f"High Traffic Alert: {'YES' if high_traffic_alert else 'NO'}")  # Update alert label

                    # If high traffic is detected, record the logs
                    if high_traffic_alert:  # If high traffic alert is true
                        self.traffic_data.append({  # Append traffic data
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),  # Record timestamp
                            "logs": traffic_logs,  # Store logs
                            "throughput": throughput,  # Store throughput
                            "latency": latency,  # Store latency
                            "cpu_usage": cpu_usage,  # Store CPU usage
                            "memory_usage": memory_usage,  # Store memory usage
                        })

                # Sleep for 1 second before updating the logs
                time.sleep(1)  # Pause for 1 second

    def toggle_monitoring(self):
        """Toggle the monitoring state."""
        self.monitoring = not self.monitoring  # Switch monitoring state
        self.toggle_button.config(text="Resume Monitoring" if not self.monitoring else "Pause Monitoring")  # Update button text

    def save_high_traffic_logs(self):
        """Save logs with high traffic alerts to a .log file when the application is closed."""
        with open("high_traffic_logs.log", "w") as log_file:  # Open log file for writing
            for entry in self.traffic_data:  # Iterate through traffic data
                log_file.write(f"Timestamp: {entry['timestamp']}\n")  # Write timestamp
                log_file.write(f"Throughput: {entry['throughput']}\n")  # Write throughput
                log_file.write(f"Latency: {entry['latency']}\n")  # Write latency
                log_file.write(f"CPU Usage: {entry['cpu_usage']}\n")  # Write CPU usage
                log_file.write(f"Memory Usage: {entry['memory_usage']}\n")  # Write memory usage
                log_file.write("Logs:\n")  # Write logs header
                for log in entry["logs"]:  # Iterate through logs
                    log_file.write(
                        f"{log['timestamp']} - {log['method']} {log['path']} (IP: {log['ip']}) - {log['response_status']}\n")  # Write log entry
                log_file.write("\n\n")  # Add spacing

    def on_close(self):
        """Handle window close event."""
        self.save_high_traffic_logs()  # Save logs on close
        self.running = False  # Stop the main loop
        self.root.destroy()  # Destroy the window


def main():
    # Define the Flask server URL
    server_url = "http://127.0.0.1:5000"  # Change this to your Flask server's URL

    root = tk.Tk()  # Create the main window
    app = IDSApp(root, server_url)  # Initialize the application

    # Handle window close safely
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # Set close protocol
    root.mainloop()  # Start the GUI loop


if __name__ == "__main__":
    main()  # Execute main function
