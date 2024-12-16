import threading  # Import threading module for concurrent execution
import requests  # Import requests module for making HTTP requests
import time  # Import time module for time-related functions
import csv  # Import csv module for handling CSV files
from datetime import datetime  # Import datetime for timestamping

# Default log file
log_file = 'traffic_log.csv'  # Specify the log file name

# Initialize the log file with headers
with open(log_file, mode='w', newline='') as file:  # Open log file in write mode
    writer = csv.writer(file)  # Create a CSV writer object
    writer.writerow(["Timestamp", "Method", "Status_Code", "Response_Time", "Requests_Per_Second"])  # Write headers

# Track request count and time window
request_count, start_time_window = 0, time.time()  # Initialize request count and start time


def log_request(method, status_code, response_time):
    """Logs the request details to a CSV file."""
    global request_count, start_time_window  # Use global variables
    current_time = time.time()  # Get the current time
    requests_per_second = request_count if current_time - start_time_window < 1 else 0  # Calculate requests per second

    with open(log_file, mode='a', newline='') as file:  # Open log file in append mode
        writer = csv.writer(file)  # Create a CSV writer object
        writer.writerow([datetime.now(), method, status_code, response_time, requests_per_second])  # Log request details

    request_count = request_count + 1 if current_time - start_time_window < 1 else 1  # Update request count
    start_time_window = current_time if current_time - start_time_window >= 1 else start_time_window  # Reset time window


def send_request(url, method, headers, data, params, timeout):
    """Sends an HTTP request and logs the response."""
    start_time = time.time()  # Record the start time
    try:
        response = requests.request(  # Send the HTTP request
            method=method.upper(), url=url, headers=headers, data=data, params=params, timeout=timeout
        )
        log_request(method, response.status_code, round(time.time() - start_time, 2))  # Log successful request
    except requests.exceptions.RequestException as e:  # Handle request exceptions
        log_request(method, "Failed", round(time.time() - start_time, 2))  # Log failed request


def simulate_traffic(url, method, headers, data, params, requests_per_second, concurrency, timeout):
    """Simulates traffic based on user-defined parameters."""
    print(f"Simulating traffic to {url} with {requests_per_second} requests per second.")  # Print simulation info
    print("Press Ctrl+C to stop.")  # Instruction to stop simulation

    interval = 1 / requests_per_second if requests_per_second > 0 else 0  # Calculate interval between requests

    def worker():  # Define worker function for threading
        send_request(url, method, headers, data, params, timeout)  # Call send_request

    try:
        while True:  # Infinite loop for continuous traffic simulation
            threads = [threading.Thread(target=worker) for _ in range(concurrency)]  # Create threads
            for thread in threads:  # Start all threads
                thread.start()
            for thread in threads:  # Wait for all threads to finish
                thread.join()
            time.sleep(interval)  # Wait for the next interval
    except KeyboardInterrupt:  # Handle keyboard interrupt
        print("\nTraffic simulation stopped.")  # Notify user of stop


def main():
    """Main function to configure traffic parameters and start simulation."""
    print("Custom Traffic Payload Generator")  # Print program title

    url = input("Enter the target URL: ").strip()  # Get target URL from user

    print("Choose the HTTP method:")  # Prompt for HTTP method
    print("1. GET")  # Option 1
    print("2. POST")  # Option 2
    print("3. PUT")  # Option 3
    print("4. DELETE")  # Option 4
    print("5. PATCH")  # Option 5
    method_choice = input("Enter your choice (1/2/3/4/5): ")  # Get method choice from user
    methods = {"1": "GET", "2": "POST", "3": "PUT", "4": "DELETE", "5": "PATCH"}  # Map choices to methods
    method = methods.get(method_choice, "GET")  # Default to GET if invalid choice

    headers = input("Enter headers as JSON (e.g., {'Content-Type': 'application/json'}): ").strip()  # Get headers
    if headers:  # If headers are provided
        try:
            headers = eval(headers)  # Evaluate headers string to dictionary
        except Exception as e:  # Handle evaluation errors
            print("Invalid headers format. Using default headers.")  # Notify user of error
            headers = {}  # Set to default

    data = input("Enter data payload (for POST/PUT/PATCH methods): ").strip()  # Get data payload

    params = input("Enter query parameters as JSON (e.g., {'key': 'value'}): ").strip()  # Get query parameters
    if params:  # If parameters are provided
        try:
            params = eval(params)  # Evaluate parameters string to dictionary
        except Exception as e:  # Handle evaluation errors
            print("Invalid query parameters format. Using default.")  # Notify user of error
            params = {}  # Set to default

    requests_per_second = float(input("Enter the desired requests per second: "))  # Get requests per second
    concurrency = int(input("Enter the number of concurrent requests: "))  # Get concurrency level
    timeout = float(input("Enter the request timeout (in seconds): "))  # Get timeout value

    simulate_traffic(url, method, headers, data, params, requests_per_second, concurrency, timeout)  # Start simulation


if __name__ == "__main__":  # Check if script is run directly
    main()  # Call main function
