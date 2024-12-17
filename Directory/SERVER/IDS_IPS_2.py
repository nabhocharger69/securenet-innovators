import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
import random


class IDSApp:
    def __init__(self, root, server_url):
        self.root = root
        self.server_url = server_url
        self.root.title("Interactive IDS/IPS Logs")
        self.running = True
        self.vulnerable_mode = False  # Toggle for vulnerability mode
        self.high_traffic_logs = []  # Store high traffic logs for file generation

        # Create widgets for the UI
        self.create_widgets()

        # Start a background thread for real-time updates
        self.update_thread = threading.Thread(target=self.update_logs)
        self.update_thread.daemon = True
        self.update_thread.start()

    def create_widgets(self):
        # Input for server IP address
        self.ip_frame = tk.Frame(self.root)
        self.ip_frame.pack(pady=5)
        tk.Label(self.ip_frame, text="Server IP Address: ").pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(self.ip_frame, width=20)
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.ip_entry.insert(0, self.server_url)

        self.apply_ip_button = tk.Button(self.ip_frame, text="Apply IP", command=self.update_server_url)
        self.apply_ip_button.pack(side=tk.LEFT, padx=5)

        # Logs display
        self.log_display = tk.Text(self.root, height=20, width=100)
        self.log_display.pack(pady=10)

        # Metrics
        self.throughput_label = tk.Label(self.root, text="Throughput: N/A")
        self.throughput_label.pack(pady=5)

        self.latency_label = tk.Label(self.root, text="Latency (ms): N/A")
        self.latency_label.pack(pady=5)

        self.cpu_usage_label = tk.Label(self.root, text="CPU Usage (%): N/A")
        self.cpu_usage_label.pack(pady=5)

        self.memory_usage_label = tk.Label(self.root, text="Memory Usage (%): N/A")
        self.memory_usage_label.pack(pady=5)

        self.high_traffic_alert_label = tk.Label(self.root, text="High Traffic Alert: N/A", fg="black")
        self.high_traffic_alert_label.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(button_frame, text="RESET", command=self.reset_settings)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.block_button = tk.Button(button_frame, text="BLOCK Flood Traffic", command=self.block_flood_traffic)
        self.block_button.pack(side=tk.LEFT, padx=5)

        self.vulnerability_button = tk.Button(button_frame, text="TOGGLE Vulnerability Mode", command=self.toggle_vulnerability)
        self.vulnerability_button.pack(side=tk.LEFT, padx=5)

    def update_server_url(self):
        """Update the server URL based on user input."""
        new_ip = self.ip_entry.get().strip()
        if new_ip.startswith("http://") or new_ip.startswith("https://"):
            self.server_url = new_ip
            self.log_display.insert(tk.END, f"\nServer URL updated to: {self.server_url}\n")
        else:
            messagebox.showerror("Invalid IP", "Please enter a valid server IP starting with 'http://' or 'https://'.")

    def fetch_traffic_data(self):
        """Fetch the traffic data from the Flask server."""
        try:
            response = requests.get(f"{self.server_url}/api/traffic")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return None

    def update_logs(self):
        """Continuously update logs and metrics."""
        while self.running:
            data = self.fetch_traffic_data()

            if data:
                traffic_logs = data["traffic_logs"]
                throughput = data["throughput"]
                latency = data["latency"]
                cpu_usage = data["cpu_usage"]
                memory_usage = data["memory_usage"]
                high_traffic_alert = False

                # Check for high traffic (>= 100 requests per second)
                request_count = len(traffic_logs)
                if request_count >= 100 and not self.vulnerable_mode:
                    high_traffic_alert = True

                # Update logs
                self.log_display.delete(1.0, tk.END)
                for log in traffic_logs:
                    log_entry = f"{log['timestamp']} - {log['method']} {log['path']} (IP: {log['ip']}) - {log['response_status']}\n"
                    self.log_display.insert(tk.END, log_entry)

                    # Save high traffic logs
                    if high_traffic_alert:
                        self.high_traffic_logs.append(log_entry)

                # Update metrics
                if throughput:
                    self.throughput_label.config(text=f"Throughput (Bytes Sent/Received): Sent: {throughput[-1]['bytes_sent']} / Received: {throughput[-1]['bytes_recv']}")
                if latency:
                    self.latency_label.config(text=f"Latency (ms): {latency[-1]:.2f}")
                if cpu_usage:
                    self.cpu_usage_label.config(text=f"CPU Usage (%): {cpu_usage[-1]:.2f}")
                if memory_usage:
                    self.memory_usage_label.config(text=f"Memory Usage (%): {memory_usage[-1]:.2f}")

                # Update high traffic alert status
                if high_traffic_alert:
                    self.high_traffic_alert_label.config(text="High Traffic Alert: YES", fg="red")
                else:
                    self.high_traffic_alert_label.config(text="High Traffic Alert: NO", fg="black")

            time.sleep(1)  # Update every second

    def block_flood_traffic(self):
        """Simulate blocking of high traffic sources."""
        try:
            response = requests.post(f"{self.server_url}/api/block")
            if response.status_code == 200:
                self.log_display.insert(tk.END, "\nFlood traffic successfully blocked!\n")
            else:
                self.log_display.insert(tk.END, "\nFailed to block traffic.\n")
        except Exception as e:
            self.log_display.insert(tk.END, f"\nError blocking traffic: {e}\n")

    def toggle_vulnerability(self):
        """Toggle the IDS/IPS vulnerability mode."""
        self.vulnerable_mode = not self.vulnerable_mode
        status = "ON" if self.vulnerable_mode else "OFF"
        self.log_display.insert(tk.END, f"\nVulnerability mode is now {status}.\n")

    def start_monitoring(self):
        """Start monitoring traffic."""
        self.running = True
        if not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_logs)
            self.update_thread.daemon = True
            self.update_thread.start()

    def stop_monitoring(self):
        """Stop monitoring traffic."""
        self.running = False
        self.log_display.insert(tk.END, "\nMonitoring stopped.\n")

    def reset_settings(self):
        """Reset all settings to their default state."""
        self.log_display.delete(1.0, tk.END)
        self.throughput_label.config(text="Throughput: N/A")
        self.latency_label.config(text="Latency (ms): N/A")
        self.cpu_usage_label.config(text="CPU Usage (%): N/A")
        self.memory_usage_label.config(text="Memory Usage (%): N/A")
        self.high_traffic_alert_label.config(text="High Traffic Alert: N/A", fg="black")
        self.high_traffic_logs = []
        self.log_display.insert(tk.END, "All settings reset to normal.\n")

    def save_high_traffic_logs(self):
        """Save high traffic logs to a .log file."""
        if self.high_traffic_logs:
            with open("high_traffic_logs.log", "w") as file:
                file.writelines(self.high_traffic_logs)

    def on_close(self):
        """Handle the close event."""
        self.stop_monitoring()
        self.save_high_traffic_logs()
        self.root.destroy()


def main():
    # Define the Flask server URL
    server_url = "http://192.168.223.33:5000/"  # Change this to your Flask server's URL

    root = tk.Tk()
    app = IDSApp(root, server_url)

    # Close the Tkinter window safely
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
