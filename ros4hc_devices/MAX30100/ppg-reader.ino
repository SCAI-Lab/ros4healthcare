/*
Arduino-MAX30100 oximetry / heart rate integrated sensor library
Copyright (C) 2016  OXullo Intersecans <x@brainrapers.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <Wire.h>
#include "MAX30100_PulseOximeter.h"
//#include "MAX30100.h"
#include <WiFi.h>
#include <esp_websocket_client.h>

#ifdef DEBUG_OCPP_WS
#define WS_INFO(x, ...) ESP_LOGI("WS", x, #__VA_ARGS__)
#define WS_ERROR(x, ...) ESP_LOGE("WS", x, #__VA_ARGS__)
#else
#define WS_INFO(x, ...) {}
#define WS_ERROR(x, ...) {}
#endif

const char* ssid = "SSID";
const char* password = "PWD";
String topic = "/hr";
WebsocketsClient client;
const char* websocketServer = "ws://172.17.0.245:9090"; // Replace with actual WebSocket server
char buffer[200];
esp_websocket_client_handle_t client;

#define REPORTING_PERIOD_MS     1000

// Sampling is tightly related to the dynamic range of the ADC.
// refer to the datasheet for further info
#define SAMPLING_RATE                       MAX30100_SAMPRATE_100HZ

// The LEDs currents must be set to a level that avoids clipping and maximises the
// dynamic range
#define IR_LED_CURRENT                      MAX30100_LED_CURR_50MA
#define RED_LED_CURRENT                     MAX30100_LED_CURR_27_1MA

// The pulse width of the LEDs driving determines the resolution of
// the ADC (which is a Sigma-Delta).
// set HIGHRES_MODE to true only when setting PULSE_WIDTH to MAX30100_SPC_PW_1600US_16BITS
#define PULSE_WIDTH                         MAX30100_SPC_PW_1600US_16BITS
#define HIGHRES_MODE                        true

// PulseOximeter is the higher level interface to the sensor
// it offers:
//  * beat detection reporting
//  * heart rate calculation
//  * SpO2 (oxidation level) calculation
PulseOximeter pox;
//MAX30100 pox;

TaskHandle_t poxTask;

uint32_t tsLastReport = 0;
bool web_connected = false;
// Callback (registered below) fired when a pulse is detected
void onBeatDetected() {
    Serial.println("Beat!");
}

void websocketEventHandler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    esp_websocket_event_data_t *data = (esp_websocket_event_data_t *)event_data;
    switch (event_id)
    {
    case WEBSOCKET_EVENT_CONNECTED:
        WS_INFO("WEBSOCKET_EVENT_CONNECTED");
        web_connected = true;
        int i = snprintf(buffer, 200, "{\"op\": \"advertise\", \"topic\": \"%s\", \"type\": \"ros4hc_msgs/HR\"}");
        sendMessage(buffer, i);
        break;
    case WEBSOCKET_EVENT_DISCONNECTED:
        WS_INFO("WEBSOCKET_EVENT_DISCONNECTED");
        web_connected = false;
        break;
    case WEBSOCKET_EVENT_DATA:
        WS_INFO("WEBSOCKET_EVENT_DATA");
        WS_INFO("Received opcode=%d", data->op_code);
        if (data->op_code == 0x08 && data->data_len == 2)
        {
            WS_INFO("Received closed message with code=%d", 256 * data->data_ptr[0] + data->data_ptr[1]);
        }
        else
        {
            WS_INFO("Received=%.*s", data->data_len, (char *)data->data_ptr);
        }
        WS_INFO("Total payload length=%d, data_len=%d, current payload offset=%d\r\n", data->payload_len, data->data_len, data->payload_offset);
        break;
    case WEBSOCKET_EVENT_ERROR:
        WS_INFO("WEBSOCKET_EVENT_ERROR");
        break;
    }
}

void sendMessage(char *data, size_t len)
{
    while (1)
    {
        if (esp_websocket_client_is_connected(client))
        {
            char toTransmit[len + 5];
            snprintf(toTransmit, len + 5, "%s", data);
            WS_INFO("Sending %s", toTransmit);
            esp_websocket_client_send_text(client, toTransmit, len, portMAX_DELAY);
            break;
        }
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}

void setup()
{
    Serial.begin(115200);

    // Initialize the PulseOximeter instance
    // Failures are generally due to an improper I2C wiring, missing power supply
    // or wrong target chip
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    Serial.print("Connecting to Wifi...");

    while(WiFi.status() != WL_CONNECTED) {
      Serial.print('.');
      delay(1000);
    }

    Serial.println(WiFi.localIP());

    esp_websocket_client_config_t websocket_cfg = {};
    websocket_cfg.uri = websocketServer;
    client = esp_websocket_client_init(&websocket_cfg);
    esp_websocket_register_events(client, WEBSOCKET_EVENT_ANY, websocketEventHandler, (void *)client);
    esp_websocket_client_start(client);
        
    Serial.print("Initializing pulse oximeter..");
    if (!pox.begin()) {
        Serial.println("FAILED");
        for(;;);
    } else {
        Serial.println("SUCCESS");
    }

    // The default current for the IR LED is 50mA and it could be changed
    //   by uncommenting the following line. Check MAX30100_Registers.h for all the
    //   available options.
    // pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);

    // Register a callback for the beat detection
    //pox.setOnBeatDetectedCallback(onBeatDetected);
    /*pox.setMode(MAX30100_MODE_SPO2_HR);
    pox.setLedsCurrent(IR_LED_CURRENT, RED_LED_CURRENT);
    pox.setLedsPulseWidth(PULSE_WIDTH);
    pox.setSamplingRate(SAMPLING_RATE);
    pox.setHighresModeEnabled(HIGHRES_MODE);*/
}

void loop() {
    // Make sure to call update as fast as possible
    pox.update();
    // Asynchronously dump heart rate and oxidation levels to the serial
    // For both, a value of 0 means "invalid"
    if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
        float hr = pox.getHeartRate();
        //float hr = 10.0;
        if (web_connected) {
            int i = snprintf(buffer, 200, "{\"op\": \"publish\", \"topic\": \"%s\", \"msg\": {\"hr\": %i}}", topic, (int)hr);
            sendMessage(buffer, i);
            Serial.print("C - ");
        }
        Serial.print("Heart rate:");
        Serial.print(hr);
        Serial.print("bpm / SpO2:");
        Serial.print(pox.getSpO2());
        Serial.println("%");

        tsLastReport = millis();
    }
}
