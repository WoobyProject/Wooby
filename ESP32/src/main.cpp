// #include "U8glib.h"
#include <U8g2lib.h>                 // by Oliver
#include "HX711.h"
#include <Wire.h>
#include <math.h>

#include "WoobyImage.h"

#include "Debugging.h"

#include "Filters/IIRFilter.hpp"
#include <RunningAverage.h>

#include <EasyButton.h>


//************************//
//*      VERSION SEL     *//
//************************//
 //#define CALIBRATED
  #define FIRST_ORDER
  #define TYPE 0

  // TYPE = 0 (PROTOTYPE)
  #if TYPE == 0
    bool B_DEBUG_MODE = true;
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = false;
    bool B_INHIB_NEG_VALS = false;
    bool B_INACTIVITY_ENABLE = false;
    #define BDEF_GOOGLE_HTTPREQ true
    bool B_GOOGLE_HTTPREQ = BDEF_GOOGLE_HTTPREQ;
    #define BDEF_SERIALPORT true
    bool B_SERIALPORT = BDEF_SERIALPORT;
    bool B_WIFI = true;
    bool B_WIFI_SMART_CONFIG = false;
    bool B_SERIALTELNET = true;
    #define BDEF_OTA true
    bool B_OTA = BDEF_OTA;
    #define BDEF_BLE true
    bool B_BLE = BDEF_BLE;
    #define BDEF_HOLD false
    bool B_HOLD = BDEF_HOLD;
  #endif

// TYPE = 3 (PROTOTYPE-connectToWiFi)
  #if TYPE == 3
    bool B_DEBUG_MODE = true;
    bool B_ANGLE_ADJUSTMENT = false;
    bool B_VCC_MNG = true;
    bool B_INHIB_NEG_VALS = false;
    bool B_INACTIVITY_ENABLE = false;
    bool B_SERIALPORT = false;
    bool B_WIFI = true;
    bool B_WIFI_SMART_CONFIG = false;
    #define B_SERIALTELNET true 
    #define B_GOOGLE_HTTPREQ false
    #define B_OTA true
    #define B_BLE true 
  #endif

    

  // TYPE = 1 (FINAL DELIVERY)
  #if TYPE == 1
    bool B_DEBUG_MODE = false;
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_INHIB_NEG_VALS = true;
    bool B_INACTIVITY_ENABLE = true;
    #define BDEF_SERIALPORT true
    bool B_SERIALPORT = BDEF_SERIALPORT;
    bool B_WIFI = true;
    bool B_WIFI_SMART_CONFIG = false;
    bool B_SERIALTELNET = false;
    #define BDEF_GOOGLE_HTTPREQ true
    bool B_GOOGLE_HTTPREQ = BDEF_GOOGLE_HTTPREQ;
    #define BDEF_OTA true
    bool B_OTA = BDEF_OTA;
    #define BDEF_BLE true
    bool B_BLE = BDEF_BLE;
    #define BDEF_HOLD true
    bool B_HOLD = BDEF_HOLD;
  #endif

#include <ArduinoJson.h>            // by Benoit Blanchon
#include <WiFi.h>
#include <WiFiClientSecure.h>
// For encryption
/*
#include <SHA256.h>
#include <rBase64.h>                //  by boseji
*/

#include "WoobyWiFi.h"

#include "OTAserver.h"

//************************//
//*      SENSOR CONF     *//
//************************//
typedef struct
{
  bool F_sensor_active;
  unsigned int clk_pin;
  unsigned int dout_pin;
} T_SensorConf;

#define NB_HX711 4
//                                                   CLK DOUT
 const T_SensorConf HX711_conf[NB_HX711] = { { true, 18, 19 },
                                             { true, 17,  5 },
                                             { true, 18, 32 },
                                             { true, 17, 33 } };

  HX711 scale[NB_HX711];

  // TBR int gain = 64;  // Reading values with 64 bits (could be 128 too) useless because gain is set in the begin call

  float MAX_GR_VALUE = 11000; // in gr
  float MIN_GR_VALUE = 5;    // in gr

  float correctedValueFiltered = 0.0;
  float displayFinalValue = 0;
  float displayFinalValue_1 = 0;

  unsigned long tBeforeMeasure[NB_HX711] = {0, 0, 0, 0};
  unsigned long tAfterMeasure[NB_HX711] = {0, 0, 0, 0};
  unsigned long tAfterAlgo[NB_HX711] = {0, 0, 0, 0};
  char arrayMeasure[8];

  //************************//
  //*  WEIGHTING ALGO CONF *//
  //************************//

    const int nMeasures = 4;
    const int nMeasuresTare = 4;

    // Definition of the coeffs for the filter
    // Remember : Te = nMeasures*100 ms
    //            b = 1 - math.exp(-Te/tau)
    //            a = math.exp(-Te/tau)
    //            tau = 1.4
    const float b =  0.24852270692472; // Te = nMeasures*100 ms
    const float a =  0.75147729307528; //

    // Filter = y/u = b*z-1(1-a)
    NormalizingIIRFilter<NB_HX711, NB_HX711, float> filterWeight[] = { {{0, b}, {1, -a}}, {{0, b}, {1, -a}}, {{0, b}, {1, -a}}, {{0, b}, {1, -a}} };

    const float FILTERING_THR = 20.0;  // in grams
    const float K_WU_to_grams = 2.07447658e-2;

    float realValue_WU[NB_HX711] = {0.0, 0.0, 0.0, 0.0};
    float realValue;
    float realValue_1;
    float realValueFiltered;
    float realValueFiltered_1;
    float relativeVal_WU_1[NB_HX711];

    float relativeVal_WU[NB_HX711] = {0.0, 0.0, 0.0, 0.0};
    float realValue_WU_MovAvg[NB_HX711] = {0.0, 0.0, 0.0, 0.0};
    float realValue_WU_Filt[NB_HX711] = {0.0, 0.0, 0.0, 0.0};

    float correctedValue = 0;
    RTC_DATA_ATTR float offset[NB_HX711] = {0.0, 0.0, 0.0, 0.0};

    bool bSync;
    unsigned long bSyncTimer = 0;
    const unsigned long BSYNC_TIME = 2000;

    bool bHold;
    unsigned long bHoldTimer = 0;
    const unsigned long BHOLD_TIME = 5000;

    const int N_WINDOW_MOV_AVG = nMeasures;
    RunningAverage weightMovAvg[NB_HX711] = { RunningAverage(N_WINDOW_MOV_AVG),
                                              RunningAverage(N_WINDOW_MOV_AVG),
                                              RunningAverage(N_WINDOW_MOV_AVG),
                                              RunningAverage(N_WINDOW_MOV_AVG) };

//************************//
//*  VCC MANAGEMENT CONF *//
//************************//

  const int PIN_VCC = 34;

  const float VCCMIN   = 5.0;         // Minimum expected Vcc level, in Volts.
  const float VCCMAX   = 7.3;         // Maximum expected Vcc level, in Volts.

  // New:
  const int N_VCC_READ = 10;
  float K_BITS_TO_VOLTS = 3.3/4095;

  const float realMeasureVcc =      7.270;
  const float realMeasureDivider =  2.355;
  const float realMeasureADC =      2.154;

  const float RATIO_VCC_DIV = realMeasureVcc/realMeasureDivider;
  const float RATIO_VCC_ADC = realMeasureVcc/realMeasureADC;
  const float RATIO_DIV_ADC = realMeasureDivider/realMeasureADC;

  float vccReadBits = 0;      // Voltage read by the ADC (in bits)
  float vccReadVolts = 0;     // Voltage read by the ADC (in Volts)
  float vccGPIO = 0;          // Real voltage on the GPIO pin (in Volts)
  float vccVolts = 0;         // Real voltage of Vcc (in Volts)
  float ratioVCCMAX = 0;      // Percentage of the read voltage in Vcc to the full charge voltage


  bool BF_VCCMNG = false;


//************************//
//*   TARE BUTTON CONF   *//
//************************//

  const int PIN_PUSH_BUTTON = 35; // TODO repetead

  unsigned long countTimeButton;

  int tareButtonStateN   = 0;
  int tareButtonStateN_1 = 0;
  int tareButtonFlank    = 0;

  unsigned long tStartTareButton = 0;
  unsigned long tEndTareButton = 0;

  /* EasyButton */
  EasyButton tareButton(PIN_PUSH_BUTTON, 50, true, true); // tareButton(BTN_PIN, debounce, pullup, invert

//************************//
//*      DISPLAY CONF    *//
//************************//

// For Arduino:
//  U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_DEV_0|U8G_I2C_OPT_NO_ACK|U8G_I2C_OPT_FAST); // Fast I2C / TWI
// For ESP32:
  U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// For ESP32, replace 'setPrintPos' by 'setCursor'.
  int state = 0;
  int setupState = 0;

  #define DISPLAY_WIDTH 128
  #define DISPLAY_HEIGHT 64
  #define FLIP_MODE 0
  #define NSTATES_SETUP 11

  bool BF_DISPLAY = false;

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

  // See https://arduinojson.org/v6/assistant/
  const int N_FIELDS_JSON = 60;
  //const size_t CAPACITY_JSON = JSON_OBJECT_SIZE(N_FIELDS_JSON) + 0; //1620
  const size_t CAPACITY_JSON = 2000; //1620
  DynamicJsonDocument genericJSON(CAPACITY_JSON);
  String genericJSONString; // TODO  create a String with the right MAX length

//************************//
//*   SERIAL COMMS CONF  *//
//************************//

  bool BF_SERIALPORT = false;

//************************//
//*     BLUETOOTH CONF   *//
//************************//

  #ifdef BDEF_BLE
    #include "BluetoothSerial.h"
    BluetoothSerial SerialBT;
    bool BF_BLUETOOTH = false;
    bool BT_CLIENT_CONNECT = false;
  #endif

//*******************************//
//*      WEIGHTING ALGORITHM    *//
//*******************************//

void myTare()
{
  int i;

  DPRINTLN("TARE starting... ");
  unsigned long bTare = millis();
  for(i=0;i < NB_HX711;i++)
  {
    if (HX711_conf[i].F_sensor_active)
    {
// TBR  scale[i].tare(nMeasuresTare);
      offset[i] = scale[i].tare(nMeasuresTare);
      DPRINT("Offset");DPRINT(i+1);DPRINT("=");DPRINTLN(offset[i]);
    }
    else
    {
    }
  }
  DPRINT("TARE time: "); DPRINT(float((millis()-bTare)/1000)); DPRINTLN(" s");

  // Reinitializing the filters
  for(i=0;i < NB_HX711;i++)
  {
    weightMovAvg[i].fillValue(0, N_WINDOW_MOV_AVG);
    filterWeight[i].reset(0);
  }
}


float correctionAlgo(float realValue){

  int realValueInt = int(realValue);
  float realValueDecim = (realValue - float(realValueInt)) ;
  float correctedValue = 0;

  // Around zero values deletion //
    if (realValue<=MIN_GR_VALUE && realValue>=-1*MIN_GR_VALUE){
      return correctedValue = 0.0;
    }

  // Round algorithm //
    if ( realValueDecim < 0.4) { correctedValue = long(realValueInt);}
    if ( realValueDecim >= 0.4 && realValueDecim <= 0.7) { correctedValue = long(realValueInt)+0.5 ; }
    if ( realValueDecim > 0.7) { correctedValue = long(realValueInt)+1; }

  return correctedValue;
}


//********************++++****//
//*   TARE BUTTON FUNCTIONS  *//
//*********************++++***//

void newTare(){
    Serial.printf("\nNew tare! \n");
    myTare();
    bHold = false;
}

void setDebugMode(){

    if (B_DEBUG_MODE){
      Serial.printf("\n\nOut of debug! \n\n");
      B_DEBUG_MODE = false;

      B_INACTIVITY_ENABLE = true;
      B_INHIB_NEG_VALS = true;
      B_SERIALTELNET = false;
      B_WIFI = false;
      B_OTA = false;
      B_BLE = false;

    }
    else{
      Serial.printf("\n\nDebug time! \n\n");
      B_DEBUG_MODE = true;

      B_INACTIVITY_ENABLE = false;
      B_INHIB_NEG_VALS = false;
      B_SERIALTELNET = true;
      B_WIFI = true;
      B_OTA = true;
      B_BLE = true;

    }
}

void couplingBLE(){
  Serial.printf("\n\nCoupling BLE! \n\n");
}

void initTareButton(){

  pinMode(PIN_PUSH_BUTTON, INPUT);

  //*         Easy Button      *//
  tareButton.begin();
  // onPressed(duration, onSequenceMatchedCallback)
  tareButton.onPressedFor(500,  newTare);            // For tare
#if TYPE == 1
  tareButton.onSequence(10, 5000, setDebugMode);        // For debug mode
  // tareButton.onPressedFor(3000, setDebugMode);          // For BLE coupling TBR
#endif

}

void newTareButtonAction()
{
  // Constinuously update the button state
  tareButton.read();
}

//************************//
//* VCC MANAGEMENT FUNCS *//
//************************//

float readPinAnalogAvg(int n){
  int sum = 0;
  for (int i=0; i< n; i++){
    sum += analogRead(PIN_VCC);
    // Serial.println(readVal);
  }
  return float(sum)/n;
}

float mapval(float x, float  in_min, float  in_max, float  out_min, float out_max){
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  }

void readVcc(){

  // Reading pin
  //Old: float(analogRead(PIN_VCC));
  vccReadBits = readPinAnalogAvg(N_VCC_READ);
  vccReadVolts = vccReadBits*K_BITS_TO_VOLTS;

  // Calulation for displaying
  vccGPIO   = vccReadVolts*RATIO_DIV_ADC;
  vccVolts  = vccReadVolts*RATIO_VCC_ADC;
  // ratioVCCMAX = min((vccVolts/VCCMAX), float(1.0));
  ratioVCCMAX = mapval(vccVolts, VCCMIN, VCCMAX, 0, 1);
  ratioVCCMAX = max(min(ratioVCCMAX, float(1.0)), float(0.0));

  /*
  Serial.printf("\nVoltage read (bits): %f", vccBits);
  Serial.printf("\nReal GPIO voltage (V): %f",   vccGPIO);
  Serial.printf("\nVCC_RATIO(V): %f",   VCC_RATIO);
  Serial.printf("\nImage to Vcc (V): %f ",   vccVolts);
  Serial.printf("\nRatio to Vcc (%%): %f \n", int(100*ratioVCCMAX));
*/


}

void setupVccMgnt(){

  analogReadResolution(12);
  analogSetWidth(12);
  analogSetPinAttenuation(PIN_VCC,ADC_11db); // ADC_11db provides an attenuation so that IN/OUT = 1 / 3.6 an input of 3 volts is reduced to 0.833 volts before ADC measurement

  readVcc();
}

//************************//
//*   DISPLAY FUNCTIONS  *//
//************************//

void setupDisplay(){

  try{
      u8g.begin();
      u8g.sleepOff();
      // Flip screen, if required
      // For Arduino:
        //u8g.setRot180();
      // For ESP32
      if (FLIP_MODE)
        Serial.println("Flipping the screen ");
      u8g.setFlipMode(FLIP_MODE);


  // Set up of the default font
    u8g.setFont(u8g2_font_6x10_tf);

 // Other display set-ups
    u8g.setFontRefHeightExtendedText();
    // For Arduino: u8g.setDefaultForegroundColor();
    u8g.setFontPosTop();

    BF_DISPLAY = false;
  }
  catch(int e){
    Serial.println("Not possible to activate the display");
    BF_DISPLAY = true;
  }
}

void initDisplay(const unsigned char * u8g_image_bits){
  u8g.firstPage();
  do {
    u8g.drawXBMP( 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, u8g_image_bits);
    // Serial.printf("Setup display value:%d\n\n",   int(float(DISPLAY_WIDTH)*float(setupState)/float(NSTATES_SETUP))  );
    u8g.drawBox(0,DISPLAY_HEIGHT-5,  int(float(DISPLAY_WIDTH)*float(setupState)/float(NSTATES_SETUP))   , 5); // (Horiz, Vert, Width, Height)
  } while( u8g.nextPage() );
}

void displayImage(const unsigned char * u8g_image_bits){
   u8g.firstPage();
   do {
       u8g.drawXBMP( 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, u8g_image_bits);
   } while( u8g.nextPage() );

   delay(4000);
}

void poweredByDisplay(void){
  Serial.println("");
  Serial.println("Displaying Powered by ...");

 // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do {
      u8g.setFont(u8g2_font_6x10_tf);
      u8g.drawStr( 30, 5, "Powered by");
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 10, 20, "Humanity");
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 40, 40, "Lab");
  }while(u8g.nextPage());

  Serial.println("Waiting 1 sec...");
  delay(1000);
  Serial.println("");
}

void sponsorsDisplay(void){
  Serial.println("");
  Serial.println("Displaying Sponsors..");

  // Set up the display
    u8g.firstPage();
    u8g.setFont(u8g2_font_osb18_tf);

  // Display loop
   do {
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 15, 25, "AIRBUS");

      u8g.setFont(u8g2_font_6x10_tf);
      u8g.drawStr( 60, 35, "&");

      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 15, 55, "MEDAIR");
   }while(u8g.nextPage());

  Serial.println("Waiting 1 sec...");
  delay(1000);
  Serial.println("");

}

void wakingUpDisplay(){
  // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do{
    u8g.setFont(u8g2_font_6x10_tf); //u8g2_font_6x10_tf
    u8g.drawStr( 45, 10, "Woooooby!");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 20, 20, "Waking up");
  }while(u8g.nextPage());
  delay(1000);
}

void sleepingDisplay(){
  // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do{
    u8g.setFont(u8g2_font_6x10_tf); //u8g2_font_6x10_tf
    u8g.drawStr( 50, 10, "zzz");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 20, 25, "Going to");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 40, 40, "sleep");
  }while(u8g.nextPage());

  delay(2000);
}

void nextStepSetup(){
  setupState++;
  initDisplay(logoWooby);
}

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

bool buildGenericJSON()
{
  int i;
  char s[21];

  for(i=0;i < NB_HX711;i++)
  {
    if (HX711_conf[i].F_sensor_active)
    {
      sprintf(s, "tBeforeMeasure%d", i+1);
      genericJSON[s] = tBeforeMeasure[i];
      sprintf(s, "tAfterMeasure%d", i+1);
      genericJSON[s] = tAfterMeasure[i];
      sprintf(s, "tAfterAlgo%d", i+1);
      genericJSON[s] = tAfterAlgo[i];
      sprintf(s, "realValue_WU%d", i+1);
      genericJSON[s] = realValue_WU[i];
      sprintf(s, "offset%d", i+1);
      genericJSON[s] = offset[i];
      sprintf(s, "relativeVal_WU%d", i+1);
      genericJSON[s] = relativeVal_WU[i];
      sprintf(s, "realValue_WU_MovAvg%d", i+1);
      genericJSON[s] = realValue_WU_MovAvg[i];
      sprintf(s, "realValue_WU_Filt%d", i+1);
      genericJSON[s] = realValue_WU_Filt[i];
    }
    else
    {
    }
  }
  genericJSON["realValueFiltered"] = realValueFiltered;
  genericJSON["realValue"] = realValue;
  genericJSON["correctedValueFiltered"] = correctedValueFiltered;

  genericJSON["bSync"] = bSync;
  #if BDEF_HOLD
    if (B_HOLD)
    {
      genericJSON["bHold"] = bHold;
    }
    else
    {
    }
  #endif
  genericJSON["vccReadBits"] = vccReadBits;
  genericJSON["vccReadVolts"] = vccReadVolts;
  genericJSON["vccGPIO"] = vccGPIO;
  genericJSON["vccVolts"] = vccVolts;
  genericJSON["ratioVCCMAX"] = ratioVCCMAX;

  genericJSON["B_DEBUG_MODE"] = B_DEBUG_MODE;

  #if B_GOOGLE_HTTPREQ
    genericJSON["B_GOOGLE_HTTPREQ"] = B_GOOGLE_HTTPREQ;
    genericJSON["BF_GOOGLE_HTTPREQ"] = BF_GOOGLE_HTTPREQ;
  #endif

  #if BDEF_SERIALPORT
    if (B_SERIALPORT){
      genericJSON["B_SERIALPORT"] = B_SERIALPORT;
      genericJSON["BF_SERIALPORT"] = BF_SERIALPORT;
    }
  #endif

  #if B_SERIALTELNET
    genericJSON["B_SERIALTELNET"] = B_SERIALTELNET;
    genericJSON["BF_SERIALTELNET"] = BF_SERIALTELNET;
  #endif

  #if B_ANGLE_ADJUSTMENT
    genericJSON["B_ANGLE_ADJUSTMENT"] = B_ANGLE_ADJUSTMENT;
    genericJSON["BF_MPU"] = BF_MPU;
  #endif

  #if B_WIFI
    genericJSON["B_WIFI"] = BF_WIFI;
    genericJSON["BF_WIFI"] = BF_WIFI;
  #endif

  return true;
}

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
    dataItem["offset"]                  = offset;
    dataItem["realValue_WU"     ]       = realValue_WU;
    dataItem["bInactive"]               = bInactive;
    dataItem["lastTimeActivity"     ]   = lastTimeActivity;

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

void printSerial()
{
  if (!B_SERIALPORT)
    return;

  if (BF_SERIALPORT)
    return;
  
  /*
  if (Serial.read()==-1)
    BF_SERIALPORT = true;
  else
    BF_SERIALPORT = false;
  */
  
  Serial.printf("\nWS");
  serializeJson(genericJSON, Serial); //serializeJsonPretty TODO this ñight be too slo, check the Telnet as example
}

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

void setUpWeightAlgorithm()
{
    int i;

    realValue_1 = 0;
    realValueFiltered = 0;
    realValueFiltered_1 = 0;
    bSync = false;
    bHold = false;
    for(i=0;i < NB_HX711;i++)
    {
      weightMovAvg[i].clear();
      weightMovAvg[i].fillValue(0, N_WINDOW_MOV_AVG); // (float)scale1.get_offset()
    }
}

void getWoobyWeight(){
    int i;
    int j;
    unsigned long time;
    float relativeValue;
    float realValueNew;

    relativeValue = 0.0f;
    for(i=0;i < NB_HX711;i++)
    {
      if (HX711_conf[i].F_sensor_active)
      {
        // Updating for synchro
        relativeVal_WU_1[i] = relativeVal_WU[i];

        // Raw weighting //
        realValue_WU[i] = (float)0.0;
        tBeforeMeasure[i] = millis();
        for(j=0;j < nMeasures;j++)
        {
          time = millis();
          realValue_WU[i] += scale[i].read();
          if (j < (nMeasures - 1))
          {
            while((millis() - time) < 100);
          }
          else
          {
          }
        }
        tAfterMeasure[i] = millis();
        realValue_WU[i] /= nMeasures;

        // TBR offset[i] = (float)scale[i].get_offset(); useless to read offset all along the reading, offset will not change
        relativeVal_WU[i] = realValue_WU[i] - offset[i];

        relativeValue += abs(relativeVal_WU[i] - relativeVal_WU_1[i]);
      }
      else
      {
      }
    }

    // Synchronization calculation
    if (relativeValue > (FILTERING_THR / K_WU_to_grams))
    {
      bSyncTimer = millis();
      bSync = true;
    }
    else
    {
      if ((millis() - bSyncTimer) > BSYNC_TIME)
      {
        bSync = false;
      }
      else
      {
        bSync = true;
      }
    }

    for(i=0;i < NB_HX711;i++)
    {
      if (HX711_conf[i].F_sensor_active)
      {
        // Moving average //
        if (bSync)
        {
          weightMovAvg[i].fillValue(relativeVal_WU[i], N_WINDOW_MOV_AVG);
          realValue_WU_MovAvg[i] = relativeVal_WU[i];
        }
        else
        {
          weightMovAvg[i].addValue(relativeVal_WU[i]);
          realValue_WU_MovAvg[i] = weightMovAvg[i].getFastAverage(); // or getAverage()
        }

        // Filtering with Arduino-Filters library
        if (bSync)
        {
          realValue_WU_Filt[i] = realValue_WU_MovAvg[i];
          filterWeight[i].reset(realValue_WU_MovAvg[i]);
        }
        else
        {
          realValue_WU_Filt[i] = filterWeight[i](realValue_WU_MovAvg[i]);
        }

        tAfterAlgo[i] = millis();
      }
      else
      {
      }
    }

    // Conversion to grams
    #ifdef CALIBRATED
    #ifdef FIRST_ORDER
      realValueNew = (float)-3.8346657784845775 +
                     (float)0.01891648 * realValue_WU_Filt[0] +
                     (float)0.01936471 * realValue_WU_Filt[1] +
                     (float)0.02002861 * realValue_WU_Filt[2] +
                     (float)0.01917123 * realValue_WU_Filt[3];
    #else
      realValueNew = (float)-2.0314661671818612 +
                     (float)1.93102010e-02  * realValue_WU_Filt[0] +
                     (float)1.91255752e-02  * realValue_WU_Filt[1] +
                     (float)2.05200649e-02  * realValue_WU_Filt[2] +
                     (float)1.96710918e-02  * realValue_WU_Filt[3] +
                     (float)-1.57030622e-08 * realValue_WU_Filt[0] * realValue_WU_Filt[0] +
                     (float)3.49965021e-08  * realValue_WU_Filt[0] * realValue_WU_Filt[1] +
                     (float)6.00372349e-08  * realValue_WU_Filt[0] * realValue_WU_Filt[2] +
                     (float)-7.19449209e-08 * realValue_WU_Filt[0] * realValue_WU_Filt[3] +
                     (float)-4.85789644e-08 * realValue_WU_Filt[1] * realValue_WU_Filt[1] +
                     (float)1.19174520e-08  * realValue_WU_Filt[1] * realValue_WU_Filt[2] +
                     (float)1.09969094e-07  * realValue_WU_Filt[1] * realValue_WU_Filt[3] +
                     (float)2.38679237e-09  * realValue_WU_Filt[2] * realValue_WU_Filt[2] +
                     (float)-5.56957203e-08 * realValue_WU_Filt[2] * realValue_WU_Filt[3] +
                     (float)-5.36102577e-08 * realValue_WU_Filt[3] * realValue_WU_Filt[3] +
                     (float)-1.11613101e-13 * realValue_WU_Filt[0] * realValue_WU_Filt[0] * realValue_WU_Filt[0] +
                     (float)-4.12549294e-13 * realValue_WU_Filt[0] * realValue_WU_Filt[0] * realValue_WU_Filt[1] +
                     (float)6.02903187e-13  * realValue_WU_Filt[0] * realValue_WU_Filt[0] * realValue_WU_Filt[2] +
                     (float)-9.89301479e-14 * realValue_WU_Filt[0] * realValue_WU_Filt[0] * realValue_WU_Filt[3] +
                     (float)-1.31332568e-12 * realValue_WU_Filt[0] * realValue_WU_Filt[1] * realValue_WU_Filt[1] +
                     (float)5.71410552e-13  * realValue_WU_Filt[0] * realValue_WU_Filt[1] * realValue_WU_Filt[2] +
                     (float)4.34111627e-12  * realValue_WU_Filt[0] * realValue_WU_Filt[1] * realValue_WU_Filt[3] +
                     (float)2.45453120e-12  * realValue_WU_Filt[0] * realValue_WU_Filt[2] * realValue_WU_Filt[2] +
                     (float)-6.45705045e-12 * realValue_WU_Filt[0] * realValue_WU_Filt[2] * realValue_WU_Filt[3] +
                     (float)7.16075241e-13  * realValue_WU_Filt[0] * realValue_WU_Filt[3] * realValue_WU_Filt[3] +
                     (float)2.04704427e-12  * realValue_WU_Filt[1] * realValue_WU_Filt[1] * realValue_WU_Filt[1] +
                     (float)-1.95076704e-12 * realValue_WU_Filt[1] * realValue_WU_Filt[1] * realValue_WU_Filt[2] +
                     (float)-4.62083231e-12 * realValue_WU_Filt[1] * realValue_WU_Filt[1] * realValue_WU_Filt[3] +
                     (float)-7.82637730e-13 * realValue_WU_Filt[1] * realValue_WU_Filt[2] * realValue_WU_Filt[2] +
                     (float)6.21342944e-12  * realValue_WU_Filt[1] * realValue_WU_Filt[2] * realValue_WU_Filt[3] +
                     (float)-6.27537909e-13 * realValue_WU_Filt[1] * realValue_WU_Filt[3] * realValue_WU_Filt[3] +
                     (float)1.25680548e-12  * realValue_WU_Filt[2] * realValue_WU_Filt[2] * realValue_WU_Filt[2] +
                     (float)9.14014872e-13  * realValue_WU_Filt[2] * realValue_WU_Filt[2] * realValue_WU_Filt[3] +
                     (float)-1.01275368e-12 * realValue_WU_Filt[2] * realValue_WU_Filt[3] * realValue_WU_Filt[3] +
                     (float)9.38532238e-13  * realValue_WU_Filt[3] * realValue_WU_Filt[3] * realValue_WU_Filt[3]; 
    #endif
    #else
      realValueNew = K_WU_to_grams * (realValue_WU_Filt[0] + realValue_WU_Filt[1] + realValue_WU_Filt[2] + realValue_WU_Filt[3]);
    #endif
    #if BDEF_HOLD
      if (B_HOLD)
      {
        if ((bHold == false) &&
            ((realValueNew < 50.0) ||
             (abs(realValueNew - realValue) > FILTERING_THR)))
        {
          bHoldTimer = millis();
          bHold = false;
        }
        else
        {
          if ((millis() - bHoldTimer) > BHOLD_TIME)
          {
            bHold = true;
          }
          else
          {
          }
        }
        if (bHold == false)
        {
          realValue = realValueNew;
          // Final correction
          correctedValueFiltered = correctionAlgo(realValue);
        }
        else
        {
        }
      }
      else
      {
      }
    #else
      realValue = realValueNew;
      // Final correction
      correctedValueFiltered = correctionAlgo(realValue);
    #endif
}

void mainDisplayWooby(){
  // Set up the display
  u8g.firstPage();

  if (correctedValueFiltered > MAX_GR_VALUE) { // Verification of the max value in grams
      do {
            u8g.setCursor(15, 15) ;
            u8g.print(" OVER");
            u8g.setCursor(15, 40) ;
            u8g.print("FLOW !");
        } while(u8g.nextPage());

  }
  else if ((correctedValueFiltered < -1*MIN_GR_VALUE)  && (B_INHIB_NEG_VALS)){ // Verification of the negative values (with threshold)
       do {
            u8g.setFont(u8g2_font_osb18_tf);
            u8g.setCursor(17, 25) ; // (Horiz, Vert)
            u8g.print(" TARE !");

            u8g.setFont(u8g2_font_6x10_tf);
            u8g.setCursor(23, 45) ; // (Horiz, Vert)
            u8g.print("Negative values");

        } while(u8g.nextPage());
  }
  else{
    // Everything is ok!!  So let's show the measurement
    do {
        // Display weight //
        u8g.setFont(u8g2_font_profont29_tr);
        u8g.setFontPosTop();
        itoa(displayFinalValue, arrayMeasure, 10);
        u8g.setCursor(DISPLAY_WIDTH/2-u8g.getStrWidth(arrayMeasure)/2, 15) ;
        u8g.print((displayFinalValue), 0);
        u8g.setFont(u8g2_font_profont15_tr);
        u8g.setFontPosTop();
        u8g.setCursor(50, 36);
        u8g.print("grams");
        // Display Hold
        #if BDEF_HOLD
          if (B_HOLD)
          {
            if (bHold)
            {
              u8g.setFont(u8g2_font_profont15_tr);
              u8g.setFontPosTop();
              u8g.setCursor(115, 50);
              u8g.print("OK");
            }
            else
            {
            }
          }
          else
          {
          }
        #endif

        if (B_DEBUG_MODE){
          u8g.setFont(u8g2_font_micro_tr);
          if (B_DEBUG_MODE){
            char bufIp[] = "192.168.000.000";
            getIp().toCharArray(bufIp, 15);
            u8g.drawStr( 46, 8, bufIp );
          }
        }

        // Display batterie levels //

        // Drawing the battery outlay
        u8g.drawLine(100,   2,    100+22, 2); // (Horiz, Vert)
        u8g.drawLine(100,   2+7,  100+22, 2+7);
        u8g.drawLine(100,   2,    100,    2+7);
        u8g.drawLine(100+22,2,    100+22, 2+7);
        u8g.drawBox(100+22+1,2+2,2, 7-4+1); // Tip of the battery

        if (false){ //BF_SERIALPORT
          u8g.setFont(u8g2_font_6x10_tf);
          u8g.setFontPosTop();
          u8g.setCursor(100, 12) ; // (Horiz, Vert)
          u8g.print("USB");
          // Shadow to show level of battery
          //u8g.drawBox(100+2,2+2,int((22-4+1)*1.0),7-4+1); // (Horiz, Vert, Width, Height)
          u8g.setFont(u8g2_font_open_iconic_embedded_1x_t);
          u8g.setFontPosTop();
          u8g.setCursor(108, 1);
          u8g.print(char(67));
        }
        else{
          // Shadow to show level of battery
          u8g.drawBox(100+2,2+2,int((22-4+1)*ratioVCCMAX),7-4+1); // (Horiz, Vert, Width, Height)

          u8g.setFont(u8g2_font_6x10_tf);
          u8g.setFontPosTop();
          u8g.setCursor(100, 12) ; // (Horiz, Vert)
          BF_VCCMNG ? u8g.print("??") : u8g.print(int(100*ratioVCCMAX));

          u8g.setFont(u8g2_font_6x10_tf);
          u8g.setFontPosTop();
          u8g.setCursor(120, 12);
          u8g.print("%");
        }


        // Display connections //
        u8g.setFont(u8g2_font_open_iconic_www_1x_t);
        u8g.drawStr( 4, 2, "Q");
        if (!B_WIFI || BF_WIFI)
          u8g.drawLine(2, 11, 11, 2);

        u8g.setFont(u8g2_font_6x10_tf);
        u8g.drawStr( 20, 3, "S");
        if (!B_SERIALPORT || BF_SERIALPORT)
          u8g.drawLine(17, 11, 26, 2);

        #ifdef B_GOOGLE_HTTPREQ
          if (B_GOOGLE_HTTPREQ){
            u8g.setFont(u8g2_font_6x10_tf);
            u8g.drawStr( 33, 3, "G");
            if(BF_GOOGLE_HTTPREQ)
              u8g.drawLine(30, 11, 39, 2);
          }
        #endif

        #ifdef BDEF_BLE
          u8g.setFont(u8g2_font_open_iconic_embedded_1x_t);
          u8g.drawStr( 33, 3, "J");
          if(!B_BLE || BF_BLUETOOTH)
            u8g.drawLine(30, 11, 39, 2);
        
        #endif

    } while(u8g.nextPage());
  }

  if (B_INACTIVITY_ENABLE){
    inactivityCheck();
    handleActionInactivity();
  }
}

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
  int i;

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

  poweredByDisplay();

  //*       SET UP  WEIGHT SENSOR       *//
  Serial.printf("Size of JSON : %d\n", CAPACITY_JSON);
  Serial.println("Setting up weight sensor...");
  for(i=0;i < NB_HX711;i++)
  {
    if (HX711_conf[i].F_sensor_active)
    {
      Serial.printf("Sensor #%d\n", i+1);
      scale[i].begin(HX711_conf[i].dout_pin, HX711_conf[i].clk_pin, 64);
      // TBR scale[i].set_gain(gain); gain is set in the call above "begin"
      // TBR scale[i].set_offset(offset[i]); useless to set offset to 0
    }
    else
    {
      Serial.printf("Sensor #%d inactive\n", i+1);
    }
  }
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
        mainDisplayWooby();

      break;
    }
    default:
    {
      Serial.println("State is not valid");
      break;
    }
  }

  }