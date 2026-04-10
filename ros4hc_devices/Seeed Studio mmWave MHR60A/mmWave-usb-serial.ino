void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, 20, 21);
}

void loop() {
  char buffer[100];
  // put your main code here, to run repeatedly:
  int ser1_waiting, ser2_waiting;
  ser1_waiting = Serial.available();
  ser2_waiting = Serial1.available();
  if (ser1_waiting) {
    Serial.readBytes(buffer, ser1_waiting);
    Serial1.write(buffer, ser1_waiting);
  }
  if (ser2_waiting) {
    Serial1.readBytes(buffer, ser2_waiting);
    Serial.write(buffer, ser2_waiting);
  }
}
