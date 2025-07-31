#include <M5Unified.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <MadgwickAHRS.h>

// Wi-Fi and UDP configuration
//const char* ssid = "LLUI_LWI";
//const char* password = "CARINg123%";
// const char* ssid = "WHILL_MR6400";
const char* ssid = "WHILL_SCAI";
const char* password = "scaiwhill";
const char* udp_ip = "192.168.0.100";  // Target IP (where ros2 node is running)
const int udp_port = 1234;             // Target UDP port (no need to change)
WiFiUDP udp;

Madgwick filter;

// IMU variables
float accelX, accelY, accelZ;
float gyroX, gyroY, gyroZ;
float roll, pitch, yaw;

// Battery management variables
unsigned long lastScreenUpdate = 0;
const unsigned long screenUpdateInterval = 5000; 
unsigned long lastDataSend = 0;
const unsigned long dataSendInterval = 100;      
bool displayOn = true;
unsigned long screenOffTimeout = 30000;          
unsigned long lastBatteryCheck = 0;
const unsigned long batteryCheckInterval = 60000; 

// Function to send IMU data via UDP
void sendIMUData() {
    StaticJsonDocument<512> doc;


    doc["id"] = "M5StickC_04";  // Unique ID change after every flash
    doc["linear_acceleration"]["x"] = accelX;
    doc["linear_acceleration"]["y"] = accelY;
    doc["linear_acceleration"]["z"] = accelZ;
    doc["angular_velocity"]["x"] = gyroX;
    doc["angular_velocity"]["y"] = gyroY;
    doc["angular_velocity"]["z"] = gyroZ;
    doc["orientation"]["roll"] = roll;
    doc["orientation"]["pitch"] = pitch;
    doc["orientation"]["yaw"] = yaw;
    doc["battery"] = M5.Power.getBatteryLevel();


    char jsonString[512];
    serializeJson(doc, jsonString);


    udp.beginPacket(udp_ip, udp_port);
    udp.write(reinterpret_cast<const uint8_t*>(jsonString), strlen(jsonString));
    udp.endPacket();
}

void updateScreen() {
    if (!displayOn) return;
    
    M5.Display.clear();
    M5.Display.setCursor(0, 0);
    M5.Display.setTextSize(1);  
    
    // Show minimal info
    M5.Display.printf("IMU: Active\n");
    M5.Display.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    M5.Display.printf("Batt: %d%%\n", M5.Power.getBatteryLevel());
    M5.Display.printf("Sending @ 10Hz\n");
    
    // Only show one set of readings
    M5.Display.println("Latest readings:");
    M5.Display.printf("A: %.1f %.1f %.1f\n", accelX, accelY, accelZ);
}

void setup() {

    auto cfg = M5.config();
    cfg.internal_imu = true;
    M5.begin(cfg);
    
    M5.Display.setBrightness(10);  
    
    // Initialize IMU
    if (!M5.Imu.isEnabled()) {
        M5.Display.clear();
        M5.Display.setCursor(0, 0);
        M5.Display.println("IMU error!");
        while (1) delay(1000);
    }

    // Connect to Wi-Fi
    M5.Display.clear();
    M5.Display.setCursor(0, 0);
    M5.Display.println("Connecting...");
    
    WiFi.mode(WIFI_STA);  
    WiFi.begin(ssid, password);
    
    int connectionAttempts = 0;
    while (WiFi.status() != WL_CONNECTED && connectionAttempts < 20) {
        delay(500);
        connectionAttempts++;
    }
    
    if (WiFi.status() != WL_CONNECTED) {
        M5.Display.clear();
        M5.Display.println("WiFi failed!");
        delay(3000);
        ESP.restart();  
    }
    

    WiFi.setSleep(true); 
    
    filter.begin(50); 
    
    udp.begin(udp_port);
    
    updateScreen();
    lastScreenUpdate = millis();
}

void loop() {
    unsigned long currentMillis = millis();
    
    M5.update();
    
    if (M5.BtnA.wasPressed()) {
        displayOn = !displayOn;
        if (displayOn) {
            M5.Display.wakeup();
            updateScreen();
        } else {
            M5.Display.sleep();
        }
    }
    
    M5.Imu.getAccel(&accelX, &accelY, &accelZ);
    M5.Imu.getGyro(&gyroX, &gyroY, &gyroZ);
    
    if (currentMillis - lastDataSend >= dataSendInterval) {
        filter.updateIMU(gyroX, gyroY, gyroZ, accelX, accelY, accelZ);
        roll = filter.getRoll();
        pitch = filter.getPitch();
        yaw = filter.getYaw();
        
        // Send IMU data
        sendIMUData();
        lastDataSend = currentMillis;
    }
    
	// update sreen
    if (displayOn && (currentMillis - lastScreenUpdate >= screenUpdateInterval)) {
        updateScreen();
        lastScreenUpdate = currentMillis;
    }
    
    // Auto turn off display
    if (displayOn && (currentMillis - lastScreenUpdate >= screenOffTimeout)) {
        displayOn = false;
        M5.Display.sleep();
    }
    
    // Check battery level periodically
    if (currentMillis - lastBatteryCheck >= batteryCheckInterval) {
        int batteryLevel = M5.Power.getBatteryLevel();
        // If battery is low (below 15%), flash warning
        if (batteryLevel < 15 && displayOn) {
            M5.Display.clear();
            M5.Display.setCursor(0, 0);
            M5.Display.setTextSize(2);
            M5.Display.println("LOW BATTERY!");
            M5.Display.printf("%d%%\n", batteryLevel);
            delay(2000);
            updateScreen();
        }
        lastBatteryCheck = currentMillis;
    }
    
    unsigned long timeToNextSend = dataSendInterval - (millis() - lastDataSend);
    if (timeToNextSend > 20) {  
        delay(10);  
    }
}
