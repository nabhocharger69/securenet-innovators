import threading
import time
import csv
from datetime import datetime
import scapy

# Default log file
log_file = 'traffic_log.csv'

# Initialize the log file with headers
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Protocol", "Src_IP", "Dst_IP", "Dst_Port", "Status", "Requests_Per_Second"])

# Track request count and time window
request_count, start_time_window = 0, time.time()


def log_request(protocol, src_ip, dst_ip, dst_port, status):
    """Logs the packet details to a CSV file."""
    global request_count, start_time_window
    current_time = time.time()
    requests_per_second = request_count if current_time - start_time_window < 1 else 0

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), protocol, src_ip, dst_ip, dst_port, status, requests_per_second])

    request_count = request_count + 1 if current_time - start_time_window < 1 else 1
    start_time_window = current_time if current_time - start_time_window >= 1 else start_time_window


def create_packet(protocol, src_ip, dst_ip, dst_port, payload):
    """Creates a packet based on user-defined parameters."""
    if protocol.upper() == "TCP":
        return Ether() / IP(src=src_ip, dst=dst_ip) / TCP(dport=dst_port) / Raw(load=payload)
    elif protocol.upper() == "UDP":
        return Ether() / IP(src=src_ip, dst=dst_ip) / UDP(dport=dst_port) / Raw(load=payload)
    else:
        raise ValueError("Unsupported protocol: Only TCP and UDP are supported.")


def send_packet(packet, protocol, src_ip, dst_ip, dst_port):
    """Sends the packet and logs the details."""
    try:
        sendp(packet, verbose=False)
        log_request(protocol, src_ip, dst_ip, dst_port, "Sent")
    except Exception as e:
        log_request(protocol, src_ip, dst_ip, dst_port, "Failed")


def simulate_traffic(protocol, src_ip, dst_ip, dst_port, payload, requests_per_second, concurrency):
    """Simulates traffic based on user-defined parameters."""
    print(f"Simulating {protocol} traffic to {dst_ip}:{dst_port} at {requests_per_second} requests per second.")
    print("Press Ctrl+C to stop.")

    interval = 1 / requests_per_second if requests_per_second > 0 else 0

    def worker():
        packet = create_packet(protocol, src_ip, dst_ip, dst_port, payload)
        send_packet(packet, protocol, src_ip, dst_ip, dst_port)

    try:
        while True:
            threads = [threading.Thread(target=worker) for _ in range(concurrency)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped.")


def main():
    """Main function to configure traffic parameters and start simulation."""
    print("Custom Traffic Payload Generator using Scapy")

    src_ip = input("Enter the source IP address: ").strip()
    dst_ip = input("Enter the destination IP address: ").strip()
    dst_port = int(input("Enter the destination port: "))

    print("Choose the protocol:")
    print("1. TCP")
    print("2. UDP")
    protocol_choice = input("Enter your choice (1/2): ")
    protocols = {"1": "TCP", "2": "UDP"}
    protocol = protocols.get(protocol_choice, "TCP")

    payload = input("Enter the payload data (e.g., 'Hello, World!'): ").strip()
    requests_per_second = float(input("Enter the desired requests per second: "))
    concurrency = int(input("Enter the number of concurrent packets: "))

    simulate_traffic(protocol, src_ip, dst_ip, dst_port, payload, requests_per_second, concurrency)


if __name__ == "__main__":
    main()
