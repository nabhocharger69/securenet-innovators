import time
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from collections import deque

# Constants
MAX_TRAFFIC = 10000  # Max packets per second
SIGNATURE_COMPLEXITY_LEVELS = [1, 2, 3]  # Complexity levels for signatures
THRESHOLD_LATENCY = 10  # Threshold for acceptable latency (ms)
TRAFFIC_SCALING_RATE = 100  # Rate at which traffic increases (packets/sec)
SIMULATION_TIME = 60  # Simulation duration in seconds

# Data Storage
throughput_data = []
latency_data = []
packet_drop_data = []
time_series = []

# Traffic generator function
def generate_traffic(rate):
    """Generates traffic at a given rate."""
    return [random.randint(100, 200) for _ in range(rate)]

# IDS/IPS simulation function
def simulate_ids_traffic(traffic, signature_complexity):
    """Simulates IDS/IPS processing traffic."""
    processed_packets = []
    dropped_packets = 0
    latency = []
    for packet in traffic:
        delay = random.uniform(0.5, 3) * signature_complexity  # Simulate delay
        if delay > THRESHOLD_LATENCY:  # Simulate packet drop condition
            dropped_packets += 1
        else:
            processed_packets.append(packet)
        latency.append(delay)
    return processed_packets, dropped_packets, np.mean(latency)

# Machine Learning for Bottleneck Prediction
def predict_failure_point(traffic_data, latency_data):
    """Uses ML to predict failure points based on traffic and latency."""
    X = np.array(traffic_data).reshape(-1, 1)
    y = np.array(latency_data)
    model = LinearRegression()
    model.fit(X, y)
    predicted_traffic = np.linspace(min(traffic_data), max(traffic_data), 100).reshape(-1, 1)
    predicted_latency = model.predict(predicted_traffic)
    return predicted_traffic, predicted_latency

# Real-time Visualization
def plot_metrics():
    plt.figure(figsize=(12, 8))
    plt.subplot(3, 1, 1)
    plt.plot(time_series, throughput_data, label="Throughput (pps)")
    plt.title("Throughput over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput")
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(time_series, latency_data, label="Latency (ms)", color="orange")
    plt.title("Latency over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Latency")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_series, packet_drop_data, label="Packet Drops", color="red")
    plt.title("Packet Drops over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Dropped Packets")
    plt.legend()

    plt.tight_layout()
    plt.show()

# Main Simulation Loop
def run_simulation():
    traffic_rate = TRAFFIC_SCALING_RATE
    start_time = time.time()

    while time.time() - start_time < SIMULATION_TIME:
        traffic = generate_traffic(traffic_rate)
        signature_complexity = random.choice(SIGNATURE_COMPLEXITY_LEVELS)
        processed, dropped, avg_latency = simulate_ids_traffic(traffic, signature_complexity)

        throughput_data.append(len(processed))
        latency_data.append(avg_latency)
        packet_drop_data.append(dropped)
        time_series.append(time.time() - start_time)

        print(f"Traffic Rate: {traffic_rate} pps | Throughput: {len(processed)} pps | Latency: {avg_latency:.2f} ms | Dropped: {dropped}")

        traffic_rate += TRAFFIC_SCALING_RATE  # Simulate load increase
        time.sleep(1)  # Delay for real-time simulation

    # Visualize Results
    plot_metrics()

    # Predict failure points using ML
    predicted_traffic, predicted_latency = predict_failure_point(throughput_data, latency_data)
    plt.plot(predicted_traffic, predicted_latency, label="Predicted Latency", color="purple")
    plt.title("Predicted Latency vs. Traffic")
    plt.xlabel("Traffic Rate (pps)")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.show()

# Run the simulation
if __name__ == "__main__":
    run_simulation()
