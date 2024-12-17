import threading
import requests
import time
import csv
from datetime import datetime
import random
import tkinter as tk
from tkinter import messagebox
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
    """Class for simulating HTTP traffic."""

    def __init__(self, url, method, headers, data, params, rps, concurrency, timeout,
                 burst_size, delay, ttl, max_packet_size, max_data_size, traffic_volume, random_packets=False):
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
        self.random_packets = random_packets

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

    def send_request(self, randomize=False):
        if self.sent_bytes >= self.traffic_volume:
            return

        if randomize:
            self.url = f"http://example.com/api/{random.randint(1, 100)}"
            self.method = random.choice(["GET", "POST", "PUT", "DELETE", "PATCH"])
            self.headers = {"Random-Header": f"Value{random.randint(1, 100)}"}
            self.data, _ = self.generate_random_payload()

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

        def random_packet_worker():
            while self.sent_bytes < self.traffic_volume:
                self.send_request(randomize=True)
                time.sleep(random.uniform(0.5, 3))

        try:
            if self.random_packets:
                threading.Thread(target=random_packet_worker).start()

            while self.sent_bytes < self.traffic_volume:
                threads = [threading.Thread(target=worker) for _ in range(self.concurrency)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                time.sleep(self.delay)
        except KeyboardInterrupt:
            print("\nTraffic simulation stopped.")


class TrafficSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Traffic Simulator")
        self.root.geometry("1200x600")  # Horizontal rectangle layout

        # Main container
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="HTTP Traffic Simulator", font=("Arial", 18)).grid(row=0, column=0, columnspan=6, pady=10)

        # Inputs
        self.add_field(main_frame, "Target URL:", "url", "http://example.com", 1)
        self.add_field(main_frame, "Headers (JSON):", "headers", "{}", 2)
        self.add_field(main_frame, "Data Payload:", "data", "", 3)
        self.add_field(main_frame, "Query Params (JSON):", "params", "{}", 4)

        self.add_field(main_frame, "RPS:", "rps", "1", 5, randomize=True)
        self.add_field(main_frame, "Concurrency:", "concurrency", "1", 6, randomize=True)
        self.add_field(main_frame, "Timeout:", "timeout", "5", 7, randomize=True)
        self.add_field(main_frame, "Burst Size:", "burst_size", "10", 8, randomize=True)
        self.add_field(main_frame, "Delay (s):", "delay", "0", 9, randomize=True)
        self.add_field(main_frame, "Max Data Size:", "max_data_size", "1000", 10, randomize=True)
        self.add_field(main_frame, "Traffic Volume:", "traffic_volume", "10000", 11, randomize=True)

        # Randomized Packets Checkbox
        self.random_packets_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Enable Randomized Packets", variable=self.random_packets_var).grid(row=12, column=0, columnspan=3, pady=10)

        # Start Button
        ttk.Button(main_frame, text="Start Simulation", command=self.start_simulation).grid(row=12, column=4, columnspan=2, pady=10)

    def add_field(self, frame, label, var_name, default, row, randomize=False):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=5)
        entry = ttk.Entry(frame, width=20)
        entry.insert(0, default)
        entry.grid(row=row, column=1, padx=5)
        setattr(self, f"{var_name}_entry", entry)

        if randomize:
            ttk.Button(frame, text="Randomize", command=lambda e=entry, v=var_name: self.randomize_input(e, v)).grid(row=row, column=2)

    def randomize_input(self, entry, var_name):
        ranges = {
            "rps": (1, 100),
            "concurrency": (1, 50),
            "timeout": (1, 10),
            "burst_size": (1, 50),
            "delay": (0, 5),
            "max_data_size": (100, 2000),
            "traffic_volume": (1000, 100000)
        }
        entry.delete(0, tk.END)
        entry.insert(0, str(random.randint(*ranges[var_name])))

    def start_simulation(self):
        try:
            simulator = TrafficSimulator(
                url=self.url_entry.get(),
                method="GET",
                headers=eval(self.headers_entry.get()),
                data=self.data_entry.get(),
                params=eval(self.params_entry.get()),
                rps=int(self.rps_entry.get()),
                concurrency=int(self.concurrency_entry.get()),
                timeout=int(self.timeout_entry.get()),
                burst_size=int(self.burst_size_entry.get()),
                delay=float(self.delay_entry.get()),
                ttl=64,
                max_packet_size=1500,
                max_data_size=int(self.max_data_size_entry.get()),
                traffic_volume=int(self.traffic_volume_entry.get()),
                random_packets=self.random_packets_var.get()
            )
            threading.Thread(target=simulator.start_simulation).start()
            messagebox.showinfo("Info", "Traffic simulation started!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulatorGUI(root)
    root.mainloop()
