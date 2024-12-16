import tkinter as tk
import requests
import threading
import time
import psutil
from collections import deque


class IDSApp:
    def __init__(self, root, server_url):
        self.root = root
        self.server_url = server_url
        self.root.title("Interactive IDS/IPS Logs")

        # Create a text box to display logs
        self.log_display = tk.Text(root, height=20, width=100)
        self.log_display.pack(pady=10)

        # Labels for displaying metrics
        self.throughput_label = tk.Label(root, text="Throughput (Bytes Sent/Received): N/A")
        self.throughput_label.pack(pady=5)

        self.latency_label = tk.Label(root, text="Latency (ms): N/A")
        self.latency_label.pack(pady=5)

        self.cpu_usage_label = tk.Label(root, text="CPU Usage (%): N/A")
        self.cpu_usage_label.pack(pady=5)

        self.memory_usage_label = tk.Label(root, text="Memory Usage (%): N/A")
        self.memory_usage_label.pack(pady=5)

        self.high_traffic_alert_label = tk.Label(root, text="High Traffic Alert: N/A")
        self.high_traffic_alert_label.pack(pady=5)

        # Button to toggle traffic monitoring
        self.toggle_button = tk.Button(root, text="Pause Monitoring", command=self.toggle_monitoring)
        self.toggle_button.pack(pady=5)

        # Internal variables
        self.running = True
        self.monitoring = True
        self.traffic_data = []  # Stores traffic data with high traffic alerts
        self.request_timestamps = deque(maxlen=100)  # Timestamps to detect bursts

        # Start the monitoring in a separate thread
        self.monitoring_thread = threading.Thread(target=self.update_logs, daemon=True)
        self.monitoring_thread.start()

    def fetch_traffic_data(self):
        """Fetch traffic data from the Flask server."""
        try:
            response = requests.get(f"{self.server_url}/api/traffic")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None

    def detect_high_traffic(self):
        """Detect high traffic bursts (50 requests in 0.5 seconds)."""
        current_time = time.time()
        self.request_timestamps.append(current_time)

        # Remove old timestamps (older than 0.5 seconds)
        while self.request_timestamps and self.request_timestamps[0] < current_time - 0.5:
            self.request_timestamps.popleft()

        # If there are 50 requests within the last 0.5 seconds, high traffic is detected
        return len(self.request_timestamps) >= 50

    def update_logs(self):
        """Fetch and display logs and metrics every second."""
        while self.running:
            if self.monitoring:
                data = self.fetch_traffic_data()

                if data:
                    traffic_logs = data["traffic_logs"]
                    throughput = data["throughput"]
                    latency = data["latency"]
                    cpu_usage = data["cpu_usage"]
                    memory_usage = data["memory_usage"]
                    high_traffic_alert = data["high_traffic_alert"]

                    # Update the display for logs
                    self.log_display.delete(1.0, tk.END)  # Clear the current text
                    for log in traffic_logs:
                        log_entry = f"{log['timestamp']} - {log['method']} {log['path']} (IP: {log['ip']}) - {log['response_status']}\n"
                        self.log_display.insert(tk.END, log_entry)

                    # Update throughput, latency, CPU, memory, and alert labels
                    if throughput:
                        self.throughput_label.config(
                            text=f"Throughput (Bytes Sent/Received): Sent: {throughput[-1]['bytes_sent']} / Received: {throughput[-1]['bytes_recv']}")
                    if latency:
                        self.latency_label.config(text=f"Latency (ms): {latency[-1]}")
                    if cpu_usage:
                        self.cpu_usage_label.config(text=f"CPU Usage (%): {cpu_usage[-1]}")
                    if memory_usage:
                        self.memory_usage_label.config(text=f"Memory Usage (%): {memory_usage[-1]}")

                    # Detect high traffic based on burst
                    if self.detect_high_traffic():
                        high_traffic_alert = True

                    self.high_traffic_alert_label.config(
                        text=f"High Traffic Alert: {'YES' if high_traffic_alert else 'NO'}")

                    # If high traffic is detected, record the logs
                    if high_traffic_alert:
                        self.traffic_data.append({
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "logs": traffic_logs,
                            "throughput": throughput,
                            "latency": latency,
                            "cpu_usage": cpu_usage,
                            "memory_usage": memory_usage,
                        })

                # Sleep for 1 second before updating the logs
                time.sleep(1)

    def toggle_monitoring(self):
        """Toggle the monitoring state."""
        self.monitoring = not self.monitoring
        self.toggle_button.config(text="Resume Monitoring" if not self.monitoring else "Pause Monitoring")

    def save_high_traffic_logs(self):
        """Save logs with high traffic alerts to a .log file when the application is closed."""
        with open("high_traffic_logs.log", "w") as log_file:
            for entry in self.traffic_data:
                log_file.write(f"Timestamp: {entry['timestamp']}\n")
                log_file.write(f"Throughput: {entry['throughput']}\n")
                log_file.write(f"Latency: {entry['latency']}\n")
                log_file.write(f"CPU Usage: {entry['cpu_usage']}\n")
                log_file.write(f"Memory Usage: {entry['memory_usage']}\n")
                log_file.write("Logs:\n")
                for log in entry["logs"]:
                    log_file.write(
                        f"{log['timestamp']} - {log['method']} {log['path']} (IP: {log['ip']}) - {log['response_status']}\n")
                log_file.write("\n\n")

    def on_close(self):
        """Handle window close event."""
        self.save_high_traffic_logs()
        self.running = False
        self.root.destroy()


def main():
    # Define the Flask server URL
    server_url = "http://127.0.0.1:5000"  # Change this to your Flask server's URL

    root = tk.Tk()
    app = IDSApp(root, server_url)

    # Handle window close safely
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
