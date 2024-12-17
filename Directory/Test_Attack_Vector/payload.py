import threading  # For concurrent execution
import requests  # For HTTP requests
import time  # For time-based calculations
import csv  # For logging to CSV
from datetime import datetime  # For timestamping
import random  # For generating random data payloads

# Default log file
LOG_FILE = 'traffic_log.csv'

# Initialize the log file with headers
with open(LOG_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Method", "Status_Code", "Response_Time", "Requests_Per_Second", "Packet_Size"])


class TrafficSimulator:
    """Class for simulating HTTP traffic with advanced features."""

    def __init__(self, url, method, headers, data, params, rps, concurrency, timeout,
                 burst_size, delay, ttl, max_packet_size, max_data_size, traffic_volume):
        """
        Initialize the traffic simulator.
        :param url: Target URL
        :param method: HTTP method
        :param headers: Request headers
        :param data: Payload
        :param params: Query parameters
        :param rps: Requests per second
        :param concurrency: Concurrent threads
        :param timeout: Request timeout
        :param burst_size: Number of requests per burst
        :param delay: Delay between bursts
        :param ttl: IP packet TTL (simulated)
        :param max_packet_size: Max packet size in bytes
        :param max_data_size: Max data size per packet
        :param traffic_volume: Total traffic volume in bytes
        """
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
        """Logs request details to a CSV file."""
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
        """Generates a random payload to simulate variable packet sizes."""
        data_size = random.randint(1, self.max_data_size)
        payload = "X" * data_size  # Simulate random data with 'X' characters
        return payload, data_size

    def send_request(self):
        """Sends a single HTTP request with random payload and logs the response."""
        if self.sent_bytes >= self.traffic_volume:
            return

        payload, data_size = self.generate_random_payload()
        if self.data:  # Use user-provided data if given, else use random payload
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
        """Starts the traffic simulation with burst and delay features."""
        print(f"\nSimulating traffic to {self.url}")
        print(f"Method: {self.method}, Burst Size: {self.burst_size}, Delay: {self.delay}s")
        print(f"Traffic Volume: {self.traffic_volume} bytes, TTL: {self.ttl}, Max Packet Size: {self.max_packet_size}")
        print("Press Ctrl+C to stop.\n")

        interval = 1 / self.rps if self.rps > 0 else 0

        def worker():
            """Worker function for threading."""
            for _ in range(self.burst_size):
                if self.sent_bytes < self.traffic_volume:
                    self.send_request()

        try:
            while self.sent_bytes < self.traffic_volume:
                threads = []
                for _ in range(self.concurrency):
                    thread = threading.Thread(target=worker)
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
                time.sleep(self.delay)  # Add delay between bursts
        except KeyboardInterrupt:
            print("\nTraffic simulation stopped.")


def get_user_input():
    """Gets and validates user inputs for advanced simulation parameters."""
    print("Custom HTTP Traffic Simulator with Advanced Packet Control\n")

    url = input("Enter the target URL: ").strip()

    print("\nChoose the HTTP method:")
    print("1. GET")
    print("2. POST")
    print("3. PUT")
    print("4. DELETE")
    print("5. PATCH")
    methods = {"1": "GET", "2": "POST", "3": "PUT", "4": "DELETE", "5": "PATCH"}
    method = methods.get(input("Enter your choice (1/2/3/4/5): ").strip(), "GET")

    headers = eval(input("Enter headers as JSON (or leave blank for default): ").strip() or "{}")
    data = input("Enter data payload (optional): ").strip()
    params = eval(input("Enter query parameters as JSON (optional): ").strip() or "{}")

    rps = float(input("Enter requests per second: ").strip())
    concurrency = int(input("Enter concurrency level (threads): ").strip())
    timeout = float(input("Enter request timeout (seconds): ").strip())

    burst_size = int(input("Enter burst size: ").strip())
    delay = float(input("Enter delay between bursts (seconds): ").strip())
    ttl = int(input("Enter IP TTL (default 64): ").strip() or 64)
    max_packet_size = int(input("Enter max packet size (bytes, default 1500): ").strip() or 1500)
    max_data_size = int(input("Enter max data size per packet (bytes, default 1000): ").strip() or 1000)
    traffic_volume = int(input("Enter total traffic volume (bytes, default 10000): ").strip() or 10_000)

    return url, method, headers, data, params, rps, concurrency, timeout, burst_size, delay, ttl, max_packet_size, max_data_size, traffic_volume


def main():
    """Main function to start the simulation."""
    params = get_user_input()
    simulator = TrafficSimulator(*params)
    simulator.start_simulation()


if __name__ == "__main__":
    main()
