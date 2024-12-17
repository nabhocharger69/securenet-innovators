import threading
import requests
import time
import csv
from datetime import datetime
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

# Default log file
LOG_FILE = 'traffic_log.csv'

# Initialize the log file with headers
with open(LOG_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Timestamp", "Method", "Status_Code", "Response_Time", "Requests_Per_Second", "Packet_Size"
    ])


class TrafficSimulator:
    """Class for simulating HTTP traffic with advanced features."""

    def __init__(self, url, method, headers, data, params, rps, concurrency, timeout,
                 burst_size, delay, ttl, max_packet_size, max_data_size, traffic_volume):
        self.url = url
        self.method = method.upper()
        self.headers = headers
        self.data = data
        self.params = params
        self.rps = rps
        self.concurrency = concurrency
        self.timeout = timeout
        self.burst_size = burst_size
        self.delay = delay
        self.ttl = ttl
        self.max_packet_size = max_packet_size
        self.max_data_size = max_data_size
        self.traffic_volume = traffic_volume
        self.sent_bytes = 0
        self.request_count = 0
        self.start_time_window = time.time()

    def log_request(self, status_code, response_time, packet_size):
        current_time = time.time()
        requests_per_second = self.request_count if current_time - self.start_time_window < 1 else 0

        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now(),
                self.method,
                status_code,
                response_time,
                requests_per_second,
                packet_size
            ])

        if current_time - self.start_time_window >= 1:
            self.request_count = 1
            self.start_time_window = current_time
        else:
            self.request_count += 1

    def generate_random_payload(self):
        data_size = random.randint(1, self.max_data_size)
        payload = "X" * data_size
        return payload, data_size

    def send_request(self):
        if self.sent_bytes >= self.traffic_volume:
            return

        payload, data_size = self.generate_random_payload()
        if self.data:
            payload = self.data[:self.max_data_size]

        start_time = time.time()
        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                data=payload,
                params=self.params,
                timeout=self.timeout
            )
            response_time = round(time.time() - start_time, 2)
            self.log_request(response.status_code, response_time, data_size)
        except requests.exceptions.RequestException:
            response_time = round(time.time() - start_time, 2)
            self.log_request("Failed", response_time, data_size)

        self.sent_bytes += data_size

    def start_simulation(self):
        def worker():
            for _ in range(self.burst_size):
                if self.sent_bytes < self.traffic_volume:
                    self.send_request()

        interval = 1 / self.rps if self.rps > 0 else 0
        try:
            while self.sent_bytes < self.traffic_volume:
                threads = []
                for _ in range(self.concurrency):
                    thread = threading.Thread(target=worker)
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
                time.sleep(self.delay)
        except KeyboardInterrupt:
            print("\nTraffic simulation stopped.")


# GUI for the Traffic Simulator
class TrafficSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Traffic Simulator")
        self.root.geometry("500x700")

        # UI Components
        ttk.Label(root, text="HTTP Traffic Simulator", font=("Arial", 16)).pack(pady=10)

        # URL Input
        ttk.Label(root, text="Target URL:").pack()
        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # HTTP Method Selection
        ttk.Label(root, text="HTTP Method:").pack()
        self.method_var = tk.StringVar(value="GET")
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.method_menu = ttk.Combobox(root, textvariable=self.method_var, values=methods)
        self.method_menu.pack(pady=5)

        # Headers Input
        ttk.Label(root, text="Headers (JSON):").pack()
        self.headers_entry = ttk.Entry(root, width=50)
        self.headers_entry.pack(pady=5)

        # Data Payload Input
        ttk.Label(root, text="Data Payload:").pack()
        self.data_entry = ttk.Entry(root, width=50)
        self.data_entry.pack(pady=5)

        # Query Parameters
        ttk.Label(root, text="Query Parameters (JSON):").pack()
        self.params_entry = ttk.Entry(root, width=50)
        self.params_entry.pack(pady=5)

        # Other Inputs
        self.add_input_field("Requests Per Second:", "rps", default=1)
        self.add_input_field("Concurrency Level:", "concurrency", default=1)
        self.add_input_field("Timeout (seconds):", "timeout", default=5)
        self.add_input_field("Burst Size:", "burst_size", default=10)
        self.add_input_field("Delay Between Bursts (seconds):", "delay", default=0)
        self.add_input_field("Max Data Size (bytes):", "max_data_size", default=1000)
        self.add_input_field("Traffic Volume (bytes):", "traffic_volume", default=10000)

        # Start Button
        self.start_button = ttk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=20)

    def add_input_field(self, label, var_name, default):
        ttk.Label(self.root, text=label).pack()
        setattr(self, var_name + "_entry", ttk.Entry(self.root))
        getattr(self, var_name + "_entry").insert(0, str(default))
        getattr(self, var_name + "_entry").pack(pady=5)

    def start_simulation(self):
        try:
            # Collect all input values
            url = self.url_entry.get()
            method = self.method_var.get()
            headers = eval(self.headers_entry.get() or "{}")
            data = self.data_entry.get()
            params = eval(self.params_entry.get() or "{}")
            rps = float(self.rps_entry.get())
            concurrency = int(self.concurrency_entry.get())
            timeout = float(self.timeout_entry.get())
            burst_size = int(self.burst_size_entry.get())
            delay = float(self.delay_entry.get())
            max_data_size = int(self.max_data_size_entry.get())
            traffic_volume = int(self.traffic_volume_entry.get())

            # Run simulation in a separate thread
            simulator = TrafficSimulator(url, method, headers, data, params, rps, concurrency,
                                         timeout, burst_size, delay, 64, 1500, max_data_size, traffic_volume)
            threading.Thread(target=simulator.start_simulation).start()
            messagebox.showinfo("Info", "Traffic simulation started!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulatorGUI(root)
    root.mainloop()
