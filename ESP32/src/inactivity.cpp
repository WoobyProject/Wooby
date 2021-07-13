#include <Arduino.h>
#include <U8g2lib.h> 
#include "HX711.h"
#include "mapping.h"
#include "version.h"
#include "inactivity.h"
#include "display.h"
#include "main.h"
#include "Debugging.h"

unsigned long lastTimeActivity = 0;
RTC_RODATA_ATTR int test = 0;

const gpio_num_t PIN_WAKEUP = GPIO_NUM_35;
const int WAKEUP_LEVEL = 0;
const float INACTIVE_THR  = 5.0;
const float MAX_INACTIVITY_TIME = 10*1000; // in milliseconds

bool bInactive = false;

void print_wakeup_reason()
{
  switch(esp_sleep_get_wakeup_cause())
  {
    case ESP_SLEEP_WAKEUP_EXT0  :     Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1  :     Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER  :    Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD  : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP  :      Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.println("Wakeup was not caused by deep sleep"); Serial.printf("Cause:%d", esp_sleep_get_wakeup_cause()); break;
  }
}

void setUpInactivity()
{
  lastTimeActivity =  millis();
  // Is this necesary? It seems it's not:
  // rtc_gpio_pulldown_en(PIN_WAKEUP)
  esp_sleep_enable_ext0_wakeup(PIN_WAKEUP, WAKEUP_LEVEL);

  // For Arduino:
  // Serial.print("CLOCK DIVISION:"); Serial.println(CLKPR);
  // pinMode(PIN_WAKEUP, INPUT_PULLUP);
  // attachInterrupt(digitalPinToInterrupt(interruptPin), wakeUp, CHANGE);

}

void updateLastTime()
{
  if ( (abs(displayFinalValue - displayFinalValue_1) > INACTIVE_THR ) || (B_DEBUG_MODE) )
  {
      lastTimeActivity =  millis();
  }
}

void handleActionInactivity()
{
  if (!bInactive)
  {
    // Waking up ...

    // Waking the screen up
    u8g.sleepOff();
    // Reseting the last time variables
    updateLastTime();
  }
  else
  {
    // Going to sleep...
    // GUI information
    sleepingDisplay();

    // Putting the screen in sleep mode
    u8g.sleepOn();

    //Putting the ESP in sleep mode (deep sleep)
    // esp_light_sleep_start(); NOT THIS ONE! We'll need to review the code !
    esp_deep_sleep_start();

    // Putting the Arduino in sleep mode
    /*set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();*/
  }
}

void inactivityCheck()
{
  // Update of last time activity
  updateLastTime();
  unsigned long runtimeNow = millis();

  // Checking inactivity
  if ((runtimeNow - lastTimeActivity) > MAX_INACTIVITY_TIME)
  {
      DEEPDPRINT("Inactive - Time diff: ");
      DEEPDPRINT((runtimeNow - lastTimeActivity)/1000);
      DEEPDPRINTLN(" s");
      bInactive = true;
  }
  else
  {
      DEEPDPRINTLN("Active: ");
      bInactive = false;
  }
}

void RTC_IRAM_ATTR esp_wake_deep_sleep(void)
{
    esp_default_wake_deep_sleep();
    // Add additional functionality here
    ets_delay_us(100);
    test++;
    //static RTC_RODATA_ATTR const char fmt_str[] = "Wake count %d\n";
    //esp_rom_printf(fmt_str, test++);
}
