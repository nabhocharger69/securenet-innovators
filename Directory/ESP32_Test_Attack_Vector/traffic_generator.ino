#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Your_SSID";       // Replace with your WiFi SSID
const char* password = "Your_PASSWORD"; // Replace with your WiFi Password
String url;  // The URL to be provided by the user

unsigned long request_count = 0;
unsigned long start_time_window = 0;

void logRequest(int status_code, float response_time) {
  unsigned long current_time = millis();
  if (current_time - start_time_window < 1000) {
    request_count++;
  } else {
    request_count = 1;
    start_time_window = current_time;
  }
  Serial.printf("Status: %d, Response Time: %.2fms, Requests This Window: %lu\n", status_code, response_time, request_count);
}

void sendRequest() {
  HTTPClient http;
  unsigned long start_time = millis();

  try {
    http.begin(url);  // Begin HTTP request to the user-provided URL
    int http_code = http.GET();  // Send HTTP GET request
    float response_time = millis() - start_time;
    if (http_code > 0) {
      logRequest(http_code, response_time);
    } else {
      logRequest(http_code, response_time);
    }
    http.end();
  } catch (...) {
    logRequest(-1, millis() - start_time);
  }
}

void simulateTraffic(int requests_per_second, int burst_size, int delay_ms) {
  Serial.printf("Simulating traffic at %d requests per second. Press RESET to stop.\n", requests_per_second);
  while (true) {
    for (int i = 0; i < burst_size; i++) {
      sendRequest();
    }
    delay(delay_ms);
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");

  Serial.println("Enter the URL or IP address to send requests to:");
  while (url.length() == 0) {
    while (Serial.available() == 0) {}
    url = Serial.readString();
    url.trim();
  }

  Serial.printf("Using URL: %s\n", url.c_str());
  Serial.println("Choose the type of traffic to simulate:");
  Serial.println("1. Normal (1 request every 2 seconds)");
  Serial.println("2. Low-Rate (50 requests in 0.5s bursts)");
  Serial.println("3. High-Rate (5000 requests per burst)");

  while (Serial.available() == 0) {}
  char choice = Serial.read();

  if (choice == '1') {
    simulateTraffic(1, 1, 2000);
  } else if (choice == '2') {
    simulateTraffic(100, 50, 500);
  } else if (choice == '3') {
    simulateTraffic(10000, 5000, 100);
  } else {
    Serial.println("Invalid choice. Please enter 1, 2, or 3.");
  }
}

void loop() {
  // Not used in this application
}
