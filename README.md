# IDS/IPS Benchmarking Solution

## Detailed Information Document uploaded in "securenet-innovators.pdf" file in the repository

## Project Overview
This project, developed by Team **SecureNet Innovators**, provides a benchmarking tool for evaluating the performance of Intrusion Detection and Prevention Systems (IDS/IPS) based on key metrics like throughput, latency, and detection accuracy. The repository also provides an IDS/IPS solution under varied conditions and uses metrics aligned with the methodologies outlined in [RFC 9411: Benchmarking Methodology for Network Security Device Performance](https://www.rfc-editor.org/info/rfc9411).

## Problem Statement
IDS/IPS devices are critical in detecting and preventing security threats. Still, they may experience performance degradation under certain conditions, such as increased traffic volume, larger packet sizes, or higher signature complexity. This project also aims to benchmark custom IDS/IPS devices, identifying potential bottlenecks and points of failure under high-load scenarios.

## Objectives
The tool benchmarks IDS/IPS devices across:
- **Throughput** - Maximum traffic rate handled without significant packet loss or delay.
- **Latency** - Delay introduced by the IDS/IPS device, particularly under high traffic.
- **Detection Accuracy** - Ability to accurately detect legitimate and malicious traffic, focusing on true and false positives.

## Key Features
1. **Traffic Profiles**: Supports various traffic conditions, including regular and attack traffic profiles.
2. **Signature Complexity**: Analyze how the complexity of signatures affects IDS/IPS performance.
3. **Latency and Packet Drop Measurement**: Provides real-time insights on packet drop and latency variations as traffic increases.
4. **Adaptive Traffic Scaling**: Dynamically adjusts traffic to simulate real-world load spikes for stress testing.
5. **Machine Learning Analysis**: Uses ML models to predict failure points and optimize IDS/IPS configuration.
6. **Interactive Visualizations**: These are real-time visualizations of throughput, latency, and accuracy, allowing for deeper performance insights.

## Solution Architecture
The solution is designed to:
- Generate varied traffic profiles to simulate real-world conditions.
- Measure throughput, latency, and packet drop rates using standards-based methodologies.
- Adjust traffic load dynamically for real-time stress tests.
- Integrate machine learning to identify performance bottlenecks and optimize IDS/IPS configurations.
- Provide interactive dashboards for visualization of performance metrics.

## Installation Process
(To be updated...)

## Timeline
**Expected Delivery Date**: 1st December 2024

## References
- [RFC 9411 - Benchmarking Methodology for Network Security Device Performance](https://www.rfc-editor.org/info/rfc9411)
- [Spirent’s resources on benchmarking network security device performance with open standards](https://www.spirent.com/blogs/benchmarking-network-security-device-performance-with-open-standards)

## Team
- **Nabhonil Bhattacharjee**
- **Sampurna Pyne**
- **Dr. Raja Karmakar**

---
