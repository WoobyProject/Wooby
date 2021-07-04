// #include "U8glib.h"
#include <U8g2lib.h>                 // by Oliver
#include <Math.h>
#include "Filters/IIRFilter.hpp"
#include <RunningAverage.h>
#include "HX711.h"
#include <ArduinoJson.h>            // by Benoit Blanchon
#include <WiFi.h>
#include <WiFiClientSecure.h>
// For encryption
/*
#include <SHA256.h>
#include <rBase64.h>                //  by boseji
*/
#include "mapping.h"
#include "version.h"
#include "main.h"
#include "battery.h"
#include "display.h"
#include "mpu6050.h"
#include "serial_com.h"
#include "tare.h"
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

  bool bInactive = false;
  const float MAX_INACTIVITY_TIME = 10*1000; // in milliseconds
  const float INACTIVE_THR  = 5.0;

  unsigned long lastTimeActivity = 0;
  const gpio_num_t PIN_WAKEUP = GPIO_NUM_35;
  const int WAKEUP_LEVEL = 0;
  esp_sleep_wakeup_cause_t wakeupReason;

//************************//
//*    GYROSCOPE CONF    *//
//************************//


//************************//
//*   TELNET COMMS CONF  *//
//************************//

#if B_SERIALTELNET==true
  #define MAX_SRV_CLIENTS 1
  WiFiServer serverTelnet(23);
  WiFiClient serverTelnetClients[MAX_SRV_CLIENTS];
  bool BF_SERIALTELNET = false;
  int nTelnetClients = 0;
#endif

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

  #ifdef BDEF_BLE
    #include "BluetoothSerial.h"
    BluetoothSerial SerialBT;
    bool BF_BLUETOOTH = false;
    bool BT_CLIENT_CONNECT = false;
  #endif

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

void print_wakeup_reason(){
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

void setUpInactivity(){
  lastTimeActivity =  millis();
  // Is this necesary? It seems it's not:
  // rtc_gpio_pulldown_en(PIN_WAKEUP)
  esp_sleep_enable_ext0_wakeup(PIN_WAKEUP, WAKEUP_LEVEL);

  // For Arduino:
  // Serial.print("CLOCK DIVISION:"); Serial.println(CLKPR);
  // pinMode(PIN_WAKEUP, INPUT_PULLUP);
  // attachInterrupt(digitalPinToInterrupt(interruptPin), wakeUp, CHANGE);

}

void updateLastTime() {
  if ( (abs(displayFinalValue - displayFinalValue_1 ) > INACTIVE_THR ) || (B_DEBUG_MODE) ) {
      lastTimeActivity =  millis();
  }
}

void handleActionInactivity(){

  if (!bInactive){
    // Waking up ...

    // Waking the screen up
    u8g.sleepOff();
    // Reseting the last time variables
    updateLastTime();
  }
  else{
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

void inactivityCheck() {

  // Update of last time activity
  updateLastTime();
  unsigned long runtimeNow = millis();

  // Checking inactivity
  if ((runtimeNow - lastTimeActivity) > MAX_INACTIVITY_TIME){
      DEEPDPRINT("Inactive - Time diff: ");
      DEEPDPRINT((runtimeNow - lastTimeActivity)/1000);
      DEEPDPRINTLN(" s");
      bInactive = true;
  }
  else{
      DEEPDPRINTLN("Active: ");
      bInactive = false;
  }
}

RTC_RODATA_ATTR int test = 0;

void RTC_IRAM_ATTR esp_wake_deep_sleep(void) {
    esp_default_wake_deep_sleep();
    // Add additional functionality here
    ets_delay_us(100);
    test++;
    //static RTC_RODATA_ATTR const char fmt_str[] = "Wake count %d\n";
    //esp_rom_printf(fmt_str, test++);

}

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

#ifdef B_GOOGLE_HTTPREQ

  bool setupGoogleComs(){
    if (!B_GOOGLE_HTTPREQ){
      Serial.printf("\nWARNING: Google comms are disabled.");
      return false;
    }

    // Verifying WiFi connection
    BF_WIFI = !checkWiFiConnection();
    if (BF_WIFI){
      Serial.printf("\nWARNING: WiFi is disabled. Google comms wiil be disabled too.");
      return false;
    }

    // Connexion to Google
    clientForGoogle.setCACert(root_ca);

  }

  void hashJSON(char* data, unsigned len) {
    // Hash encryption of the JSON
    sha.resetHMAC(key, sizeof(key));
    sha.update(data, len);
    sha.finalizeHMAC(key, sizeof(key), hmacResult, sizeof(hmacResult));
    DPRINTLN("DataSize :" + String(len));
    DPRINTLN(data);
    DPRINTLN("HashSize :" + String(sha.hashSize( )));
    DPRINTLN("BlockSize:" + String(sha.blockSize()));
    sha.clear();

  }

  String buildJson(){

    Serial.println("IP ADDRESS");
    Serial.println(getIp());

    dataItem["tBeforeMeasure"     ]     = tBeforeMeasure;
    dataItem["tAfterMeasure"     ]      = tAfterMeasure;
    dataItem["IPadress" ]               = getIp();
    dataItem["realValueFiltered"     ]  = realValueFiltered;
    dataItem["correctedValueFiltered"]  = correctedValueFiltered;
    dataItem["bSync"     ]              = bSync;
    dataItem["calibrationFactor"     ] = calibrationFactor;
    dataItem["offset"]                  = offset;
    dataItem["realValue_WU"     ]       = realValue_WU;
    dataItem["bInactive"]               = bInactive;
    dataItem["lastTimeActivity"     ]   = lastTimeActivity;
    dataItem["myAx"]                    = myAx;
    dataItem["myAy"]                    = myAy;
    dataItem["myAz"]                    = myAz;
    dataItem["thetadeg"]                = thetadeg;
    dataItem["phideg"]                  = phideg;
    dataItem["myTmp"]                   = myTmp;
    dataItem["TEMPREF"]                 = TEMPREF;
    dataItem["MODEL"]                   = MODEL;

    char name[] = "Wooby";
    // strcat(ARDUINO_BOARD,name);
    dataItem["ThisBoard"] =  name; //<char*>

    // Put the json in a string
    String jsonStr;
    serializeJson(dataItem, jsonStr);
    // Put the json string in char array
    char chBuf[jsonStr.length()];
    jsonStr.toCharArray(chBuf, jsonStr.length()+1);

    DPRINTLN("jsonStr :" + String(jsonStr));
    DPRINTLN("chBuf   :" + String(chBuf  ));
    DPRINTLN("jsonStr length:" + String(jsonStr.length()));
    DPRINTLN("chBuf   length:" + String(sizeof(chBuf   )));

    // Hashing JSON ??
    hashJSON(chBuf, sizeof(chBuf));
    rbase64.encode((char*)hmacResult);

    String resultHash = String(rbase64.result());
    DPRINTLN("Hash String: ");
    DPRINTLN(resultHash);

    String completeJSON = "{\"HMACRes\":\"" + resultHash + "\",\"Data\":" + jsonStr + "}";
    String payLoad      = "tag=DataESP&value=" + completeJSON;

    DPRINTLN("payload: ");
    DPRINTLN(payLoad);

    return payLoad;

  }

  bool sendJson(){
    String payLoad = buildJson();

    // Connexion to the host
    DPRINTLN("Connecting to ");
    DPRINTLN(host);

    if (!clientForGoogle.connect(host, port)){
      ERRORPRINTLN("Connection failed.");
      return false;
    }

    try{
      String postRequest =   "POST "  + String(uri)  + " HTTP/1.1\r\n" +
                            "Host: " + String(host) + "\r\n" +
                            "Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n" +
                        //  "Content-Type: application/json; utf-8\r\n" +
                            "Content-Length: " + payLoad.length() + "\r\n" + "\r\n" + payLoad;

      DPRINTLN("Post request: ");
      DPRINTLN(postRequest);

      // Sending the final string
      clientForGoogle.print(postRequest);
      clientForGoogle.stop();
      return true;
    }
    catch(int e){
      ERRORPRINT("Post request not succcessful");
      ERRORPRINT(e);
      return false;
    }
  }

  bool sendDataToGoogle(){
    // Verify the activation
    if (!B_GOOGLE_HTTPREQ){
      return false;
    }

    if (countForGoogleSend == N_GSHEETS){
      sendJson();
      countForGoogleSend = 0;
    }
    else{
      countForGoogleSend++;
    }
  }

#endif

//***************************//
//* SERIAL COMMS FUNCTIONS  *//
//***************************//


//***************************//
//* SERIAL TELNET FUNCTIONS *//
//***************************//

#ifdef B_SERIALTELNET

  bool setupTelnet() {

    if (!B_SERIALTELNET){
      Serial.print("WARNING: Telnet is is turned off. Telnet won't work");
      return false;
    }

    // Verifying WiFi connection
    if (!B_WIFI){
      Serial.print("WARNING: WiFi is turned off. Telnet won't work");
      return false;
    }
    BF_WIFI = !checkWiFiConnection();
    if (BF_WIFI){
      Serial.printf("\nWARNING: WiFi failed. Telnet won't work.");
      return false;
    }

    serverTelnet.begin();
    serverTelnet.setNoDelay(true);
    Serial.print("Ready to use Telnet ");
    Serial.println(WiFi.localIP());
    return true;
  }

  bool checkTelnetClients(){

    int i; // Correction TO DO! A variable should keep track of the numnber of clientes

    // Check for new clients
    if (serverTelnet.hasClient()) {
      Serial.printf("\nNew client request!\n");
      for(i = 0; i < MAX_SRV_CLIENTS; i++){
          //find free/disconnected spot
          if (!serverTelnetClients[i] || !serverTelnetClients[i].connected()){
            if(serverTelnetClients[i]) serverTelnetClients[i].stop();
            serverTelnetClients[i] = serverTelnet.available();
            if (!serverTelnetClients[i]){Serial.println("Client communication broken");}
            Serial.printf("\nNew telnet client(%d) \n", i);
            Serial.println(serverTelnetClients[i].remoteIP());
            nTelnetClients++;
            break;
          }
      }
      if (i >= MAX_SRV_CLIENTS) {
          //no free/disconnected spot so reject
          Serial.printf("\nWARNING: Maximum of telnet clients reached!\n");
          serverTelnet.available().stop();
      }

    }

    for(i = 0; i < MAX_SRV_CLIENTS; i++){
      // if (serverTelnetClients[i].connected())
        //Serial.printf("\nClient %d - Connected: %d -  IP: %s \n", i, serverTelnetClients[i].connected(), ip2String(serverTelnetClients[i].remoteIP()).c_str() );
    }

    return true;

  }

  void printSerialTelnet(){

  if (!B_SERIALTELNET)
    return;

  checkTelnetClients();

  // DPRINTF("\nLength minified JSON: \t%d", measureJson(genericJSON));
  // DPRINTF("\nLength prettified JSON: \t%d\n", measureJsonPretty(genericJSON));
  for(int i = 0; i < MAX_SRV_CLIENTS; i++){
    if (serverTelnetClients[i] && serverTelnetClients[i].connected()){
      serverTelnetClients[i].print("WT");
      String output;
      serializeJson(genericJSON, output);
      serverTelnetClients[i].print(output);
      // serializeJson(genericJSON, serverTelnetClients[i]); //serializeJsonPretty
      // serverTelnetClients[i].printf("\n"); Unnecessary, the message already has a /r/n at the end
      delay(100);
    }
  }
}

#endif

//***************************//
//*   BLUETOOTH FUNCTIONS   *//
//***************************//

#ifdef BDEF_BLE 

  void bluetoothCallback(esp_spp_cb_event_t event, esp_spp_cb_param_t *param)
  {
    if(event == ESP_SPP_SRV_OPEN_EVT)
    {
        Serial.println("Connection established");
        BT_CLIENT_CONNECT = true;
    }
    else if(event == ESP_SPP_CLOSE_EVT)
    {
        Serial.println("Connection closed");
        BT_CLIENT_CONNECT = false;
        ESP.restart();
    }
    /*
    else if(event == ESP_SPP_DATA_IND_EVT)
    {
        Serial.println("Data received");
        String response = bluetoothReadLine();
        if(response=="")
        {
            Serial.println("EMPTY");
        }
    }
    else if(event == ESP_SPP_WRITE_EVT)
    {
        Serial.println("Write operation complete");
    }
    */
  }
  
  bool setupBluetooth(){

    SerialBT.begin("Wooby", false); //Bluetooth device name
    BF_BLUETOOTH = false; // TODO !
    // SerialBT.register_callback(bluetoothCallback);

    return true;
  }

  void printSerialBluetooth(){
    
    if (BF_BLUETOOTH)
      return;

    if (!SerialBT.hasClient())
      return;
    
    // Sending the message via bluetooth
    SerialBT.print(genericJSONString);
    delay(50);
    
  }
#endif

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
