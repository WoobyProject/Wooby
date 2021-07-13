// #include "U8glib.h"
#include <U8g2lib.h>                 // by Oliver
#include <Math.h>
#include "Filters/IIRFilter.hpp"
#include <RunningAverage.h>
#include "HX711.h"
#include <ArduinoJson.h>            // by Benoit Blanchon
#include "mapping.h"
#include "version.h"
#include "main.h"
#include "battery.h"
#include "bluetooth_com.h"
#include "display.h"
#include "http_com.h"
#include "inactivity.h"
#include "mpu6050.h"
#include "serial_com.h"
#include "tare.h"
#include "telnet_com.h"
#include "weight.h"
#include "WoobyImage.h"
#include "WoobyWiFi.h"
#include "OTAserver.h"
#include "Debugging.h"

//************************//
//*      VERSION SEL     *//
//************************//


//************************//
//*      SENSOR CONF     *//
//************************//

  HX711 scale;

  // Model choice
  #if MODEL == 1
    float calibrationFactor = 42.0000;
  #endif

  #if MODEL == 2
    float calibrationFactor = 42.7461;
  #endif

  #if MODEL == 3
    // OLD BOOT LOADER
    float calibrationFactor = 61.7977;
  #endif

  #if MODEL == 4
    float calibrationFactor = 38.5299;
  #endif

  #if MODEL == 5
    float calibrationFactor = 61.7977;
  #endif

  int gain = 64;  // Reading values with 64 bits (could be 128 too)

  float displayFinalValue = 0;
  float displayFinalValue_1 = 0;

  //************************//
  //*  WEIGHTING ALGO CONF *//
  //************************//

    float correctedValue = 0;

//************************//
//*   LOAD SENSOR ADJ    *//
//************************//

  float TEMPREF = 26.0;

//************************//
//*  VCC MANAGEMENT CONF *//
//************************//


//************************//
//*   TARE BUTTON CONF   *//
//************************//

  unsigned long countTimeButton;

  int tareButtonStateN   = 0;
  int tareButtonStateN_1 = 0;
  int tareButtonFlank    = 0;

  unsigned long tStartTareButton = 0;
  unsigned long tEndTareButton = 0;

//************************//
//*      DISPLAY CONF    *//
//************************//

// For ESP32, replace 'setPrintPos' by 'setCursor'.
  int state = 0;

//************************//
//*    INACTIVITY CONF   *//
//************************//

  esp_sleep_wakeup_cause_t wakeupReason;

//************************//
//*    GYROSCOPE CONF    *//
//************************//


//************************//
//*   TELNET COMMS CONF  *//
//************************//


//************************//
//*       JSON CONF      *//
//************************//

  String genericJSONString; // TODO  create a String with the right MAX length

//************************//
//*   SERIAL COMMS CONF  *//
//************************//


//************************//
//*     BLUETOOTH CONF   *//
//************************//


  //************************//
  //* GYRO/ACCEL FUNCTIONS *//
  //************************//


//*******************************//
//*      WEIGHTING ALGORITHM    *//
//*******************************//

void myTare(){
  DPRINTLN("TARE starting... ");
  unsigned long bTare = millis();
  scale.tare(nMeasuresTare);
  DPRINT("TARE time: "); DPRINT(float((millis()-bTare)/1000)); DPRINTLN(" s");

  // Reinitializing the filters
  weightMovAvg.fillValue(0, N_WINDOW_MOV_AVG);
  filterWeight.reset(0);

  // Reading reference temperature
  readMPU();
  TEMPREF = myTmp;
  DPRINT("Reference Temp: "); DPRINT(TEMPREF); DPRINTLN(" C");
}

//********************++++****//
//*   TARE BUTTON FUNCTIONS  *//
//*********************++++***//

void couplingBLE(){
  Serial.printf("\n\nCoupling BLE! \n\n");
}

//************************//
//* VCC MANAGEMENT FUNCS *//
//************************//


//************************//
//*   DISPLAY FUNCTIONS  *//
//************************//


//***************************//
//*  INACTIVITY FUNCTIONS   *//
//***************************//


//**************************//
//* GENERIC JSON FUNCTIONS *//
//**************************//


String json2String(DynamicJsonDocument theJSON) {
  String theString;
  serializeJson(theJSON, theString);
  return theString;
}

//**************************//
//* HTTP REQUEST FUNCTIONS *//
//**************************//


//***************************//
//* SERIAL COMMS FUNCTIONS  *//
//***************************//


//***************************//
//* SERIAL TELNET FUNCTIONS *//
//***************************//

//***************************//
//*   BLUETOOTH FUNCTIONS   *//
//***************************//


//*************************//
//*    MACRO FUNCTIONS    *//
//*************************//



//************************//
//*       SET UP        *//
//************************//

/*
void partitionTable(){

  size_t ul;
  esp_partition_iterator_t _mypartiterator;
  const esp_partition_t *_mypart;
  ul = spi_flash_get_chip_size(); Serial.print("Flash chip size: "); Serial.println(ul);
  Serial.println("Partiton table:");
  _mypartiterator = esp_partition_find(ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_ANY, NULL);
  if (_mypartiterator) {
    do {
      _mypart = esp_partition_get(_mypartiterator);
      printf("%x - %x - %x - %x - %s - %i\r\n", _mypart->type, _mypart->subtype, _mypart->address, _mypart->size, _mypart->label, _mypart->encrypted);
    } while (_mypartiterator = esp_partition_next(_mypartiterator));
  }

  esp_partition_iterator_release(_mypartiterator);
  _mypartiterator = esp_partition_find(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_ANY, NULL);
  if (_mypartiterator) {
    do {
      _mypart = esp_partition_get(_mypartiterator);
      printf("%x - %x - %x - %x - %s - %i\r\n", _mypart->type, _mypart->subtype, _mypart->address, _mypart->size, _mypart->label, _mypart->encrypted);
      } while (_mypartiterator = esp_partition_next(_mypartiterator));
  }
  esp_partition_iterator_release(_mypartiterator);

}

*/

void setup(void) {

  Serial.begin(115200);
  unsigned long setUpTime =  millis();

  Serial.printf("\n\nTest value: %d\n\n", test);
  esp_set_deep_sleep_wake_stub(&esp_wake_deep_sleep);
  
  if(wakeupReason == 0){ // Wooby is initializing
    Serial.println("--- Microcontroller data ---");
    Serial.printf("Flash size: %d bytes\n", ESP.getFlashChipSize());
    Serial.printf("SDK version: %s bytes\n", ESP.getSdkVersion());
    
    Serial.println("");
  }

  //*       INACTIVITY MANAGEMENT      *// 
  wakeupReason = esp_sleep_get_wakeup_cause();
  print_wakeup_reason();

  //*          SCREEN SETUP          *//
  setupDisplay();

  //*          WELCOME MESSAGE          *//
  if(wakeupReason == 2){ // Wooby is waking up after inactiviy
    Serial.println("Wooby waking up!");     // wakingUpDisplay();
    state = 3; // Forcing state to measurement display
  }
  else{
    Serial.println("Hello! I'm Wooby!! ");
    Serial.println("Initializing to measure tons of smiles ... ");
    // initDisplay(logoWooby);
    // displayImage(logoWooby);
    state = 0;
  }

  //*       SET UP  WEIGHT SENSOR       *//
  Serial.println("Setting up weight sensor...");
  scale.begin(DOUT, CLK);
  scale.set_gain(gain);
  scale.set_scale(calibrationFactor);
  scale.set_offset(offset);
  nextStepSetup();


  //*         ACCELEROMETER           *//
  Serial.println("Setting up accelerometer sensor...");
  setupMPU();
  readMPU();  // Read the info for initializing vars and availability
  nextStepSetup();

  //*          FILTERING           *//
  Serial.println("Setting up filtering ...");
  setUpWeightAlgorithm();
  nextStepSetup();

  //*          INACTIVITY          *//
  Serial.println("Setting up inactivity check ...");
  setUpInactivity();
  nextStepSetup();

  //*          TARE BUTTON         *//
  Serial.println("Setting up tare button ...");
  initTareButton();
  nextStepSetup();

  //*          AUTO TARE           *//
  if(wakeupReason!=2){
      Serial.println("Setting up the autotare ...");
      myTare();
  }
  nextStepSetup();

  //*          VCC MANAGEMENT      *//
  Serial.println("Setting up Vcc management ...");
  setupVccMgnt();
  nextStepSetup();

  //*         WIFI CONNECTION        *//
  Serial.println("Setting up WiFi ...");
  BF_WIFI = !setupWiFi();
  nextStepSetup();

  //*          GOOGLE COMS         *//
  
  #ifdef B_GOOGLE_HTTPREQ
    Serial.println("Setting up Google comms ...");
    // TODO ! Create a Google Coms Failure boolean
    setupGoogleComs();
  #endif
  nextStepSetup();

  //*          SERIAL TELNET       *//
  #ifdef B_SERIALTELNET
    Serial.println("Setting up Telnet Serial ... ");
    BF_SERIALTELNET = !setupTelnet();
  #endif
  nextStepSetup();

  //*       SERIAL BLUETOOTH       *//
  #ifdef BDEF_BLE
    Serial.println("Setting up BLE Serial ... ");
    BF_BLUETOOTH = !setupBluetooth();
  #endif
  nextStepSetup();

  //*          OTA SERVER      *//
  #ifdef BDEF_OTA
    Serial.println("Setting up OTA ... ");
    // TODO ! Create a OTA Failure boolean
    setupOTA();
  #endif
  nextStepSetup();

  
  unsigned long setUpTimeEnd =  millis();
  Serial.println("Total setup time: " + String(float((setUpTimeEnd-setUpTime))/1000) + " s");

}

//************************//
//*        LOOP         *//
//************************//

void loop(void) {

  //*  READING OF SERIAL ENTRIES   *//
    if(Serial.available())
    {
      char temp = Serial.read();
      switch(temp){
      case '+': calibrationFactor += 0.01;
                scale.set_scale(calibrationFactor);
                break;
      case '-': calibrationFactor -= 0.01;
                scale.set_scale(calibrationFactor);
                break;
      case 't': myTare();
                break;
      case 'r': ESP.restart();
                break;
      default:
                break;
      }
    }

  //*      INACTIVITY MANAGEMENT   *//
  if(esp_sleep_get_wakeup_cause()==2){ // Wooby is waking up after inactiviy
    state=3;
  }

  //*         MAIN SWITCH          *//

  switch (state) {
    case 0:
            state++;
    break;
    case 1:
            // sponsorsDisplay();
            /* for (int i=0; i<10; i++){
              clockShoot(i, 10);
              delay(1000);
            }
            */
            state++;
    break;

    case 2:
            // Forcing the last time of activity
            lastTimeActivity =  millis();

            // Displaying and weighting is about to begin
            Serial.println("DATA START");
            state++;

    break;
    case 3:
    {

      // Main display loop

        // Tare button //
        newTareButtonAction();

        //  Vcc management  //
        readVcc();

        // Weighting //
        getWoobyWeight();

        // Creating the JSON
        buildGenericJSON();
        genericJSONString = json2String(genericJSON);

        // Serial monitor outputs  //
        #ifdef BDEF_SERIALPORT
          if(B_SERIALPORT)
            printSerial();
        #endif
        
        // Serial.printf("\n Free heap: %d", ESP.getFreeHeap()); // getSketchSize getFreeSketchSpace
        // Serial.printf("\n Skecth size: %d", ESP.getSketchSize());
        // Serial.printf("\n Vcc: %d", ESP.getVcc());

        // Google sheet data Sending  //
        #ifdef B_GOOGLE_HTTPREQ
          if (B_GOOGLE_HTTPREQ){
          // unsigned long tBeforeGoogle = millis();
          sendDataToGoogle();
          // unsigned long tAfterGoogle  = millis();
          // Serial.printf("%d ms to send data to Google",tAfterGoogle-tBeforeGoogle);
          }
        #endif

        // Serial Telnet outputs  //
        #ifdef B_SERIALTELNET
          if(B_SERIALTELNET){
          // unsigned long tBeforeTelnet = millis();
          printSerialTelnet();
          // unsigned long tAfterTelnet  = millis();
          // Serial.printf("%d ms to send data thru Telnet",tAfterTelnet-tBeforeTelnet);
          }
        #endif

        // OTA server   //
        #ifdef BDEF_OTA
          if (B_OTA)
            serverOTA.handleClient();
        #endif

        #ifdef BDEF_BLE
          if (B_BLE)
            printSerialBluetooth();
        #endif

        // Updating for inactivity check
        displayFinalValue_1 = displayFinalValue;
        displayFinalValue   = correctedValueFiltered;

        //     Displaying     //
        mainDisplayWooby(displayFinalValue);

      break;
    }
    default:
    {
      Serial.println("State is not valid");
      break;
    }
  }

  }
