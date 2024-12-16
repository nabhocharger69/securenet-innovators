from scapy.all import *
import threading
import time
import csv
from scapy.all import *
import threading
import time
import csv
from datetime import datetime

# Target server details
target_ip = "127.0.0.1"
target_port = 80
log_file = 'traffic_log_scapy.csv'

# Initialize the log file with headers
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Packet_Type", "Packet_Status", "Response_Time", "Packets_Per_Second"])

# Track packet count and time window
packet_count, start_time_window = 0, time.time()
total_data_transferred = 0


def log_packet(packet_type, status, response_time, data_size):
    global packet_count, start_time_window, total_data_transferred
    current_time = time.time()
    packets_per_second = packet_count if current_time - start_time_window < 1 else 0

    total_data_transferred += data_size

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), packet_type, status, response_time, packets_per_second])

    packet_count = packet_count + 1 if current_time - start_time_window < 1 else 1
    start_time_window = current_time if current_time - start_time_window >= 1 else start_time_window


def send_packet(ttl, max_packet_size, max_data_size):
    start_time = time.time()
    try:
        # Generate payload with the specified maximum data size
        payload = Raw(load=("X" * min(max_data_size, max_packet_size - 40)))  # 40 bytes for IP/TCP headers
        # Build and send the packet
        packet = IP(dst=target_ip, ttl=ttl) / TCP(dport=target_port, flags="S") / payload
        response = sr1(packet, timeout=2, verbose=False)

        if response and response.haslayer(TCP) and response.getlayer(TCP).flags == "SA":
            log_packet("SYN", "Success", round(time.time() - start_time, 2), len(payload))
        else:
            log_packet("SYN", "No Response", round(time.time() - start_time, 2), len(payload))
    except Exception as e:
        log_packet("SYN", f"Failed: {e}", round(time.time() - start_time, 2), 0)


def simulate_traffic(packet_rate, burst_size=1, delay=1, ttl=64, max_packet_size=1500, max_data_size=1000,
                     traffic_volume=10_000):
    print(f"Simulating traffic. Total traffic volume: {traffic_volume} bytes. Press Ctrl + C to stop.")
    try:
        total_sent = 0
        while total_sent < traffic_volume:
            threads = []
            for _ in range(burst_size):
                if total_sent >= traffic_volume:
                    break
                thread = threading.Thread(target=send_packet, args=(ttl, max_packet_size, max_data_size))
                threads.append(thread)
                total_sent += min(max_data_size, max_packet_size - 40)

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            time.sleep(delay)

        print(f"\nTraffic simulation complete. Total data transferred: {total_data_transferred} bytes.")
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped.")


if _name_ == "_main_":
    packet_rate = float(input("Enter packet rate (packets per second): "))
    burst_size = int(input("Enter burst size: "))
    delay = float(input("Enter delay between bursts (seconds): "))
    ttl = int(input("Enter IP TTL (default 64): ") or 64)
    max_packet_size = int(input("Enter maximum packet size in bytes (default 1500): ") or 1500)
    max_data_size = int(input("Enter maximum data size per packet in bytes (default 1000): ") or 1000)
    traffic_volume = int(input("Enter total traffic volume in bytes (default 10,000): ") or 10_000)

    simulate_traffic(packet_rate=packet_rate, burst_size=burst_size, delay=delay, ttl=ttl,
                     max_packet_size=max_packet_size, max_data_size=max_data_size, traffic_volume=traffic_volume)

from datetime import datetime

# Target server details
target_ip = "127.0.0.1"
target_port = 80
log_file = 'traffic_log_scapy.csv'

# Initialize the log file with headers
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Packet_Type", "Packet_Status", "Response_Time", "Packets_Per_Second"])

# Track packet count and time window
packet_count, start_time_window = 0, time.time()


def log_packet(packet_type, status, response_time):
    global packet_count, start_time_window
    current_time = time.time()
    packets_per_second = packet_count if current_time - start_time_window < 1 else 0

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), packet_type, status, response_time, packets_per_second])

    packet_count = packet_count + 1 if current_time - start_time_window < 1 else 1
    start_time_window = current_time if current_time - start_time_window >= 1 else start_time_window


def send_syn_packet():
    start_time = time.time()
    try:
        # Build and send SYN packet
        syn_packet = IP(dst=target_ip) / TCP(dport=target_port, flags="S")
        response = sr1(syn_packet, timeout=2, verbose=False)

        if response and response.haslayer(TCP) and response.getlayer(TCP).flags == "SA":
            log_packet("SYN", "Success", round(time.time() - start_time, 2))
        else:
            log_packet("SYN", "No Response", round(time.time() - start_time, 2))
    except Exception as e:
        log_packet("SYN", f"Failed: {e}", round(time.time() - start_time, 2))


def simulate_traffic(packet_rate, burst_size=1, delay=1):
    print(f"Simulating traffic at {packet_rate} packets per second. Press Ctrl + C to stop.")
    try:
        while True:
            threads = [threading.Thread(target=send_syn_packet) for _ in range(burst_size)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped.")


if __name__ == "__main__":
    packet_rate = float(input("Enter packet rate (packets per second): "))
    burst_size = int(input("Enter burst size: "))
    delay = float(input("Enter delay between bursts (seconds): "))

    simulate_traffic(packet_rate=packet_rate, burst_size=burst_size, delay=delay)