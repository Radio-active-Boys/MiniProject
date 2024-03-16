#include <WiFi.h>

void setup() {
Serial.begin(115200);

// Set WiFi to station mode and disconnect from an AP if it was previously connected
WiFi.mode(WIFI_STA);
WiFi.disconnect();

Serial.println("Scanning for WiFi networks...");
delay(1000);

// Start WiFi scan
int numNetworks = WiFi.scanNetworks();

if (numNetworks == 0) {
Serial.println("No WiFi networks found");
} else {
Serial.print("Number of WiFi networks found: ");
Serial.println(numNetworks);

// Print the details of each network found
for (int i = 0; i < numNetworks; ++i) {
Serial.print("SSID: ");
Serial.println(WiFi.SSID(i));

Serial.print("MAC Address: ");
Serial.println(WiFi.BSSIDstr(i));

Serial.print("Signal Strength (RSSI): ");
Serial.println(WiFi.RSSI(i));
Serial.println(" dBm");
//Serial.print("dBM ");
Serial.println("-----------------------");
}
}
}

void loop() {
// Nothing to do here
}
