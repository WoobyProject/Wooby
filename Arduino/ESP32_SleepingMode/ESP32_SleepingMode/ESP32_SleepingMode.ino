void setup() {
    Serial.begin(115200);
    Serial.println("setup");
}

void loop() {
    Serial.println(millis());
    
    esp_sleep_enable_timer_wakeup(3000000); //5 seconds
    int ret = esp_light_sleep_start();
    Serial.print("light_sleep:");
    Serial.println(ret);
}
