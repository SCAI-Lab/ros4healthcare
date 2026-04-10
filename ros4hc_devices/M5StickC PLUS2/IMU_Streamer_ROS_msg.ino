#include <M5Unified.h>
#include <WiFi.h>
#include <ArduinoWebsockets.h>

#include <ArduinoJson.h>
#include <MadgwickAHRS.h>

// Wi-Fi and UDP configuration
using namespace websockets;

const char* ssid = "SSID";
const char* password = "PWD";
String topic = "/IMU_001";
String frame_id = "IMU_001";
WebsocketsClient client;
const char* websocketServer = "ws://172.17.0.245:9090"; // Replace with actual WebSocket server
Madgwick filter;

// IMU variables
float accelX, accelY, accelZ;
float gyroX, gyroY, gyroZ;
float roll, pitch, yaw;

void connectWebSocket() {
    M5.Lcd.println("Connecting to WebSocket server...");
    if (client.connect(websocketServer)) {
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setCursor(10, 10);
        
        M5.Lcd.println("Connected to WebSocket");
        //Advertise IMU
        char buffer[200];  // Ensure the buffer is large enough
        snprintf(buffer, sizeof(buffer), "{\"op\": \"advertise\", \"topic\": \"%s\", \"type\": \"sensor_msgs/Imu\"}", topic);
        client.send(buffer);

    } else {
        M5.Lcd.fillScreen(BLACK);
        M5.Lcd.setCursor(10, 10);
        M5.Lcd.println("WebSocket connection failed");
    }

}

// Function to send IMU data via UDP
void sendIMUData() {
  float www = 1.0;
  String jsonString = "{"
  "\"op\": \"publish\", "
    "\"topic\": \"" + topic + "\", "
    "\"msg\": {"
        "\"header\": {\"frame_id\": \"" + frame_id + "\"},"
        "\"linear_acceleration\": {"
            "\"x\": " + String(accelX, 6) + ", \"y\": " + String(accelY, 6) + ", \"z\": " + String(accelZ, 6) + 
        "},"
        "\"angular_velocity\": {"
            "\"x\": " + String(gyroX, 6) + ", \"y\": " + String(gyroY, 6) + ", \"z\": " + String(gyroZ, 6) + 
        "},"
        "\"orientation\": {"
            "\"x\": " + String(roll, 6) + ", \"y\": " + String(pitch, 6) + ", \"z\": " + String(yaw, 6) + ", \"w\": " + String(www, 6) + 
        "}"
    "}"
"}";
    client.send(jsonString);
}

void printToScreen(const char* message) {
    M5.Display.clear();
    M5.Display.setCursor(0, 0);
    M5.Display.setTextSize(2);
    M5.Display.println(message);
}

void setup() {
    // Initialize M5Stick
    auto cfg = M5.config();
    cfg.internal_imu = true;
    cfg.internal_rtc = true;
    M5.begin(cfg);

    // Initialize IMU
    if (!M5.Imu.isEnabled()) {
        printToScreen("IMU error!");
        while (1) delay(1000);
    }

    // Connect to Wi-Fi
    printToScreen("Connecting WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    printToScreen("WiFi connected");
    delay(1000);

    // Display IP address on screen
    M5.Display.clear();
    M5.Display.setCursor(0, 0);
    M5.Display.setTextSize(2);
    M5.Display.println("IP:");
    M5.Display.println(WiFi.localIP());
    
    filter.begin(100);  // Set filter update rate to 100 Hz
    connectWebSocket();

    
}

void loop() {
    // Read IMU data
    M5.Imu.getAccel(&accelX, &accelY, &accelZ);
    M5.Imu.getGyro(&gyroX, &gyroY, &gyroZ);
    filter.updateIMU(gyroX, gyroY, gyroZ, accelX, accelY, accelZ);
    roll = filter.getRoll();
    pitch = filter.getPitch();
    yaw = filter.getYaw();
    //M5.Imu.getAttitude(&gyroX, &gyroY, &gyroZ);
    // Display current IMU data on the screen
    M5.Display.clear();
    M5.Display.setCursor(0, 0);
    M5.Display.setTextSize(2);
    M5.Display.println("Accel:");
    M5.Display.printf("X: %.2f\n", accelX);
    M5.Display.printf("Y: %.2f\n", accelY);
    M5.Display.printf("Z: %.2f\n", accelZ);
    M5.Display.println("Gyro:");
    M5.Display.printf("X: %.2f\n", gyroX);
    M5.Display.printf("Y: %.2f\n", gyroY);
    M5.Display.printf("Z: %.2f\n", gyroZ);
    M5.Display.println("Orientation:");
    M5.Display.printf("X: %.2f\n", roll);
    M5.Display.printf("Y: %.2f\n", pitch);
    M5.Display.printf("Z: %.2f\n", yaw);

    // Send IMU data every 20ms
    sendIMUData();
    delay(100);
}
