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

  #define MODEL 5
  // MODEL 1 : Arduino - Wooby 1
  // MODEL 2 : ESP32 - Wooby 2
  // MODEL 3 : Arduino - Unknown
  // MODEL 4 : Arduino - Unknown
  // MODEL 5 : ESP32 - Wooby Xtrem

  #define TYPE 3

  // TYPE = 0 (PROTOTYPE)
  #if TYPE==0
    bool B_DEBUG_MODE = true;
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = false;
    bool B_DISPLAY_ANGLES = true;
    bool B_DISPLAY_ACCEL = true;
    bool B_INHIB_NEG_VALS = false;
    bool B_INACTIVITY_ENABLE = false;
    bool B_GOOGLE_HTTPREQ = true;
    bool B_SERIALPORT = true;
    bool B_SERIALTELNET = true;
    bool B_OTA = true;
  #endif

// TYPE = 3 (PROTOTYPE-connectToWiFi)
  #if TYPE==3
    bool B_DEBUG_MODE = true;
    bool B_ANGLE_ADJUSTMENT = false;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = false;
    bool B_DISPLAY_ANGLES = true;
    bool B_DISPLAY_ACCEL = true;
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
  #if TYPE==1
    bool B_DEBUG_MODE = false;
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = true;
    bool B_DISPLAY_ANGLES = false;
    bool B_DISPLAY_ACCEL = false;
    bool B_INHIB_NEG_VALS = true;
    bool B_INACTIVITY_ENABLE = true;
    bool B_GOOGLE_HTTPREQ = true;
    bool B_SERIALPORT = true;
    bool B_SERIALTELNET = true;
    bool B_OTA = false;
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
  #define DOUT 19     // For Arduino 6
  #define CLK  18     // For Arduino 5

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

  float MAX_GR_VALUE = 11000; // in gr
  float MIN_GR_VALUE = 5;    // in gr

  float correctedValueFiltered = 0;
  float displayFinalValue = 0;
  float displayFinalValue_1 = 0;

  unsigned long tBeforeMeasure = 0;
  unsigned long tAfterMeasure = 0;
  unsigned long tAfterAlgo = 0;

  char arrayMeasure[8];

  //************************//
  //*  WEIGHTING ALGO CONF *//
  //************************//

    const int nMeasures = 7;
    const int nMeasuresTare = 7;

    // Definition of the coeffs for the filter
    // Remember : Te = nMeasures*100 ms
    //            b = 1 - math.exp(-Te/tau)
    //            a = math.exp(-Te/tau)
    //            tau = 1.4
    const float b =  0.3915; // Te = nMeasures*100 ms
    const float a =  0.6085; //

    // Filter = y/u = b*z-1(1-a)
    NormalizingIIRFilter<2, 2, float> filterWeight = {{0, b}, {1, -a}};

    const float FILTERING_THR = 20;  // in grams

    float realValue_WU = 0;
    float realValue;
    float realValue_1;
    float realValueFiltered;
    float realValueFiltered_1;
    float relativeVal_WU_1;

    float relativeVal_WU = 0;
    float realValue_WU_AngleAdj = 0;
    float realValue_WU_MovAvg = 0;
    float realValue_WU_Filt = 0;

    float correctedValue = 0;
    RTC_DATA_ATTR float offset = 0;

    bool bSync;
    unsigned long bSyncTimer = 0 ;
    const unsigned long BSYNC_TIME = 2000;

    const int N_WINDOW_MOV_AVG = nMeasures;
    RunningAverage weightMovAvg(N_WINDOW_MOV_AVG);

//************************//
//*   LOAD SENSOR ADJ    *//
//************************//

  float TEMPREF = 26.0;

  float const calib_theta_2 = -0.00014;

  // Model choice
  #if MODEL <= 4
    float K_MYAX_X = -1; float K_MYAX_Y = 0; float K_MYAX_Z = 0;
    float K_MYAY_X =  0; float K_MYAY_Y = 1; float K_MYAY_Z = 0;
    float K_MYAZ_X =  0; float K_MYAZ_Y = 0; float K_MYAZ_Z = 1;
  #endif

  #if MODEL == 5
    float K_MYAX_X =  0; float K_MYAX_Y = 0; float K_MYAX_Z = 1;
    float K_MYAY_X = -1; float K_MYAY_Y = 0; float K_MYAY_Z = 0;
    float K_MYAZ_X =  0; float K_MYAZ_Y = 1; float K_MYAZ_Z = 0;
  #endif


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

  #define DISPLAY_WIDTH 128
  #define DISPLAY_HEIGHT 64

  bool BF_DISPLAY = false;

//************************//
//*    INACTIVITY CONF   *//
//************************//

  bool bInactive = false;
  const float MAX_INACTIVITY_TIME = 60*1000; // in milliseconds
  const float INACTIVE_THR  = 5.0;

  unsigned long lastTimeActivity = 0;
  const gpio_num_t PIN_WAKEUP = GPIO_NUM_27; // GPIO_NUM_27
  const int WAKEUP_LEVEL = 1;
  esp_sleep_wakeup_cause_t wakeupReason;

//************************//
//*    GYROSCOPE CONF    *//
//************************//

  const int MPU_ADDR=0x68;
  const float pi = 3.1416;
  int16_t Ax,Ay,Az,Tmp,Gx,Gy,Gz;
  float myAx, myAy, myAz, myTmp, myGx, myGy, myGz;
  float thetadeg, phideg ;

  const float MAX_THETA_VALUE = 10;
  const float MAX_PHI_VALUE = 10;

  bool BF_MPU=false;


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
  const int N_FIELDS_JSON = 36;
  const size_t CAPACITY_JSON = JSON_OBJECT_SIZE(N_FIELDS_JSON) + 0; //1620
  DynamicJsonDocument genericJSON(CAPACITY_JSON);
  String genericJSONString; // TODO  create a String with the right MAX length

//************************//
//*   SERIAL COMMS CONF  *//
//************************//

  bool BF_SERIALPORT = false;

//************************//
//*     BLUETOOTH CONF   *//
//************************//

  #if B_BLE == true 
    #include "BluetoothSerial.h"
    BluetoothSerial SerialBT;
    bool BF_BLUETOOTH = false;
    bool BT_CLIENT_CONNECT = false;
  #endif

  //************************//
  //* GYRO/ACCEL FUNCTIONS *//
  //************************//

  void setupMPU(){

      Wire.begin();

   // Waking up the chip
      Wire.beginTransmission(MPU_ADDR); // Begins a transmission to the I2C slave (GY-521 board)
      Wire.write(0x6B); // PWR_MGMT_1 register (Power management)
      Wire.write(0b00000000); // set to zero (wakes up the MPU-6050)
      Wire.endTransmission(true);

    // Setting up the FS of the gyroscope (+-200 deg/s)
      Wire.beginTransmission(MPU_ADDR); // Begins a transmission to the I2C slave (GY-521 board)
      Wire.write(0x1B); // PWR_MGMT_1 register (Power management)
      Wire.write(0b00000000); // set to zero (wakes up the MPU-6050)
      Wire.endTransmission(true);

    // Setting up the FS of the accelerometer (+-2 g)
      Wire.beginTransmission(MPU_ADDR); // Begins a transmission to the I2C slave (GY-521 board)
      Wire.write(0x1B); // PWR_MGMT_1 register (Power management)
      Wire.write(0b00000000); // set to zero (wakes up the MPU-6050)
      Wire.endTransmission(true);
  }

  void readMPU(){

    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B);
    Wire.endTransmission(false);

    uint8_t errorRF = Wire.requestFrom(MPU_ADDR,14,true);

    if(errorRF){
      BF_MPU = false;

      Ax =  Wire.read()<<8 | Wire.read(); // reading registers: 0x3B and 0x3C
      Ay =  Wire.read()<<8 | Wire.read(); // reading registers: 0x3D and 0x3E
      Az =  Wire.read()<<8 | Wire.read(); // reading registers: 0x3F and 0x40
      Tmp = Wire.read()<<8 | Wire.read(); // reading registers: 0x41 and 0x42
      Gx =  Wire.read()<<8 | Wire.read(); // reading registers: 0x43 and 0x44
      Gy =  Wire.read()<<8 | Wire.read(); // reading registers: 0x45 and 0x46
      Gz =  Wire.read()<<8 | Wire.read(); // reading registers: 0x47 and 0x48

      myAx = (K_MYAX_X*float(Ax)+K_MYAX_Y*float(Ay)+K_MYAX_Z*float(Az))/16384;
      myAy = (K_MYAY_X*float(Ax)+K_MYAY_Y*float(Ay)+K_MYAY_Z*float(Az))/16384;
      myAz = (K_MYAZ_X*float(Ax)+K_MYAZ_Y*float(Ay)+K_MYAZ_Z*float(Az))/16384;

      myGx =    float(Gx)/131;
      myGy =    float(Gy)/131;
      myGz =    float(Gz)/131;

      myTmp = Tmp/340.00+36.53;
    }
    else{
      // Serial.println("ERROR: Reading MPU");
      BF_MPU = true;
    }
  }

  void angleCalc(){

      readMPU(); // This function also updates BF_MPU
        // Keep in mind that atan2() handles the zero div
      phideg = (180/pi)*atan2(myAy,myAz);
      thetadeg =   (180/pi)*atan2(-1*myAx, sqrt(pow(myAz,2) + pow(myAy,2)));

  }

  void angleAdjustment(){

    angleCalc(); // This function also updates BF_MPU
    if(!BF_MPU && B_ANGLE_ADJUSTMENT){
        realValue_WU_AngleAdj = relativeVal_WU/(1+calib_theta_2*pow(thetadeg, 2));
    }
    else{
    realValue_WU_AngleAdj = relativeVal_WU;
    }
  }

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


float correctionAlgo(float realValue){

  int realValueInt = int(realValue);
  float realValueDecim = (realValue - float(realValueInt)) ;
  float correctedValue = 0;

  // Around zero values deletion //
    if (realValue<MIN_GR_VALUE && realValue>-1*MIN_GR_VALUE){
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
}

void setDebugMode(){
    Serial.printf("\n\nDebug time! \n\n");
    B_DEBUG_MODE = true;
}

void couplingBLE(){
  Serial.printf("\n\nCoupling BLE! \n\n");
}

void initTareButton(){

  pinMode(PIN_PUSH_BUTTON, INPUT);

  //*         Easy Button      *//
  tareButton.begin();
  // onSequence(number_of_presses, sequence_timeout, onSequenceMatchedCallback);
  tareButton.onSequence(1,  2000,  newTare);            // For tare
  tareButton.onSequence(10, 5000, setDebugMode);        // For debug mode
  tareButton.onPressedFor(3000, couplingBLE );          // For BLE coupling

}

void newTareButtonAction()
{
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

float mapval( float x, float  in_min, float  in_max, float  out_min, float out_max){
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
      Serial.println("Flipping the screen ");
      u8g.setFlipMode(0);


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

void displayImage( const unsigned char * u8g_image_bits){
   u8g.firstPage();
   do {
       u8g.drawXBMP( 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, u8g_image_bits);
   } while( u8g.nextPage() );

   // Let us see that baby face ! :)
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
      u8g.drawStr( 30, 15, "Powered by");
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 10, 40, "Humanity");
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 40, 60, "Lab");
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
    u8g.drawStr( 55, 10, "zzz");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 30, 25, "Going to");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 45, 40, "sleep");
  }while(u8g.nextPage());

  delay(2000);
}

//***************************//
//*  INACTIVITY FUNCTIONS   *//
//***************************//

void print_wakeup_reason(){
  switch(esp_sleep_get_wakeup_cause())
  {
    case 1  : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case 2  : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case 3  : Serial.println("Wakeup caused by timer"); break;
    case 4  : Serial.println("Wakeup caused by touchpad"); break;
    case 5  : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.println("Wakeup was not caused by deep sleep"); break;
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
  if (abs(displayFinalValue - displayFinalValue_1 ) > INACTIVE_THR ){
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

//**************************//
//* GENERIC JSON FUNCTIONS *//
//**************************//

bool buildGenericJSON(){

  genericJSON["tBeforeMeasure"] = tBeforeMeasure;
  genericJSON["tAfterMeasure"] = tAfterMeasure;
  genericJSON["tAfterAlgo"] = tAfterAlgo;

  genericJSON["realValue_WU"] = realValue_WU;
  genericJSON["OFFSET"] = offset;
  genericJSON["calibrationFactor"] = calibrationFactor;

  genericJSON["relativeVal_WU"] = relativeVal_WU;
  genericJSON["realValue_WU_AngleAdj"] = realValue_WU_AngleAdj;
  genericJSON["realValue_WU_MovAvg"] = realValue_WU_MovAvg;
  genericJSON["realValue_WU_Filt"] = realValue_WU_Filt;

  genericJSON["realValue"] = realValue;
  genericJSON["realValueFiltered"] = realValueFiltered;
  genericJSON["correctedValueFiltered"] = correctedValueFiltered;

  genericJSON["myAx"] = myAx;
  genericJSON["myAy"] = myAy;
  genericJSON["myAz"] = myAz;
  genericJSON["myGx"] = myGx;
  genericJSON["myGy"] = myGy;
  genericJSON["myGz"] = myGz;

  genericJSON["thetadeg"] = thetadeg;
  genericJSON["phideg"] = phideg;
  genericJSON["myTmp"] = myTmp;

  genericJSON["bSync"] = bSync;
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

  #if B_SERIALPORT
    genericJSON["B_SERIALPORT"] = B_SERIALPORT;
    genericJSON["BF_SERIALPORT"] = BF_SERIALPORT;
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

#if B_GOOGLE_HTTPREQ

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

#if B_SERIALTELNET==true

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

#if B_BLE == true 

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

void setUpWeightAlgorithm(){
    realValue_1 = 0;
    realValueFiltered = 0;
    realValueFiltered_1 = 0;
    bSync = false;

    weightMovAvg.clear();
    weightMovAvg.fillValue(0, N_WINDOW_MOV_AVG); // (float)scale.get_offset()
}

void getWoobyWeight(){

    // Updating for synchro
    relativeVal_WU_1 = relativeVal_WU;

    // Raw weighting //
    tBeforeMeasure = millis();
    realValue_WU = scale.read_average(nMeasures);
    tAfterMeasure = millis();

    offset = (float)scale.get_offset();
    relativeVal_WU = realValue_WU - offset;

    // Synchronization calcualtion

    if (abs(relativeVal_WU-relativeVal_WU_1) > FILTERING_THR*scale.get_scale()){
      bSyncTimer = millis();
      bSync = true;
    }
    else{
      if (millis()-bSyncTimer > BSYNC_TIME){
        bSync = false;}
      else{
        bSync = true;
      }
    }

    // Angles correction //
    angleAdjustment();

    // Moving average //
    if (bSync){
      weightMovAvg.fillValue(realValue_WU_AngleAdj, N_WINDOW_MOV_AVG);
      realValue_WU_MovAvg = realValue_WU_AngleAdj;
    }
    else{
      weightMovAvg.addValue(realValue_WU_AngleAdj);
      realValue_WU_MovAvg = weightMovAvg.getFastAverage(); // or getAverage()
    }

    // Filtering with Arduino-Filters library
    if (bSync){
      realValue_WU_Filt = realValue_WU_MovAvg;
      filterWeight.reset(realValue_WU_MovAvg);
    }
    else{
      realValue_WU_Filt = filterWeight(realValue_WU_MovAvg);
    }


    // Conversion to grams //
    realValue = realValue_WU_Filt/scale.get_scale(); // (realValue_WU_AngleAdj)/scale.get_scale();
    /*
    correctedValue = correctionAlgo(realValue); // NOT USED!!!!!

    // Filtering  //

      // Filtering for the real value //
      realValueFilterResult = filtering(realValue, realValue_1, realValueFiltered_1);
      bSync = realValueFilterResult.bSync;
      realValueFiltered = realValueFilterResult.yk;

      // Updating for filtering
      realValueFiltered_1 = realValueFiltered;
      realValue_1 = realValue;
    */

    // Final correction  //
    correctedValueFiltered = correctionAlgo(realValue);

    tAfterAlgo = millis();
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
  else if ((abs(thetadeg) > MAX_THETA_VALUE || abs(phideg) > MAX_PHI_VALUE ) && (B_LIMITED_ANGLES)){ // Verification of the maximum allowed angles
       do {
            u8g.setFont(u8g2_font_osb18_tf);
            u8g.setCursor(17, 30) ; // (Horiz, Vert)
            u8g.print(" OUPS !");

            u8g.setFont(u8g2_font_6x10_tf);
            u8g.setCursor(23, 45) ; // (Horiz, Vert)
            u8g.print("Wooby NOT flat");

        } while(u8g.nextPage());
  }
  else{
    // Everything is ok!!  So let's show the measurement
    do {
        // Display weight //
        u8g.setFont(u8g2_font_osb18_tf);
        u8g.setFontPosTop();
        itoa(displayFinalValue, arrayMeasure, 10);
        u8g.setCursor(DISPLAY_WIDTH/2-u8g.getStrWidth(arrayMeasure)/2, 10) ;
        u8g.print((displayFinalValue), 0);


        u8g.setFont(u8g2_font_osb18_tf);
        u8g.setFontPosTop();
        u8g.setCursor(30, 25);
        u8g.print("grams");

        // Display MPU values //
        if (B_DISPLAY_ANGLES){
          // Display trust region //
          u8g.setFont(u8g2_font_6x10_tf);
          u8g.setFontPosBottom();
          u8g.setCursor(5, DISPLAY_HEIGHT-2);
          BF_MPU? u8g.print("???"): u8g.print(int(thetadeg), 10);


          u8g.setFont(u8g2_font_6x10_tf);
          u8g.setFontPosBottom();
          u8g.setCursor(55, DISPLAY_HEIGHT-2);
          BF_MPU? u8g.print("???"): u8g.print(String(int(myTmp)) + "("+ String(int(TEMPREF)) + ")");

          u8g.setFont(u8g2_font_6x10_tf);
          u8g.setFontPosBottom();
          u8g.setCursor(100, DISPLAY_HEIGHT-2);
          BF_MPU? u8g.print("???"): u8g.print(int(phideg), 10);
        }

        if (B_DISPLAY_ACCEL){
          u8g.setFont(u8g2_font_6x10_tf);

          u8g.setCursor(4, 24);
          BF_MPU? u8g.print("???"):u8g.print(roundf(myAx*100.0)/100.0);

          u8g.setCursor(4, 31);
          BF_MPU? u8g.print("???"):u8g.print(roundf(myAy*100.0)/100.0);

          u8g.setCursor(4, 38);
          BF_MPU? u8g.print("???"):u8g.print(roundf(myAz*100.0)/100.0);

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

            // For bluetooh u8g2_font_open_iconic_embedded_1x_t char(74)

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

          #if (B_GOOGLE_HTTPREQ)
            u8g.setFont(u8g2_font_6x10_tf);
            u8g.drawStr( 33, 3, "G");
            if(BF_GOOGLE_HTTPREQ)
              u8g.drawLine(30, 11, 39, 2);
          #endif

          #if B_BLE == true 
            u8g.setFont(u8g2_font_6x10_tf);
            u8g.drawStr( 33, 3, "B");
            if(BF_BLUETOOTH)
              u8g.drawLine(30, 11, 39, 2);
          #endif

          u8g.setFont(u8g2_font_micro_tr);
          if (B_DEBUG_MODE){
            char bufIp[] = "192.168.000.000";
            getIp().toCharArray(bufIp, 15);
            u8g.drawStr( 46, 3, bufIp );
          }



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

void setup(void) {

  Serial.begin(115200);
  unsigned long setUpTime =  millis();

  if(wakeupReason == 0){ // Wooby is initializing
    Serial.println("--- Microcontroller data ---");
    Serial.printf("Flash size: %d bytes\n", ESP.getFlashChipSize());
    Serial.println("");
  }

  //*       INACTIVITY MANAGEMENT      *//
  wakeupReason = esp_sleep_get_wakeup_cause();
  // print_wakeup_reason();

  //*          SCREEN SETUP          *//
  setupDisplay();

  //*          WELCOME MESSAGE          *//
  if(wakeupReason == 2){ // Wooby is waking up after inactiviy
    Serial.println("Wooby waking up!");     // wakingUpDisplay();
  }
  else{
    Serial.println("Hello! I'm Wooby!! ");
    Serial.println("Initializing to measure tons of smiles ... ");
    displayImage(logoWooby);
  }

  //*       SET UP  WEIGHT SENSOR       *//
  Serial.println("Setting up weight sensor...");
  scale.begin(DOUT, CLK);
  scale.set_gain(gain);
  scale.set_scale(calibrationFactor);
  scale.set_offset(offset);


  //*         ACCELEROMETER           *//
  Serial.println("Setting up accelerometer sensor...");
  setupMPU();
  readMPU();  // Read the info for initializing vars and availability

  //*          FILTERING           *//
  setUpWeightAlgorithm();

  //*          INACTIVITY          *//
  setUpInactivity();

  //*          TARE BUTTON         *//
  initTareButton();

  //*          AUTO TARE           *//
  if(wakeupReason!=2){
      myTare();
  }

  //*          VCC MANAGEMENT      *//
  Serial.printf("\nSetup Vcc management\n");
  setupVccMgnt();

  //*         WIFI CONNECTION        *//
  Serial.printf("\nSetup WiFi\n");
  BF_WIFI = !setupWiFi();

  //*          GOOGLE COMS         *//
  
  #if B_GOOGLE_HTTPREQ
    Serial.printf("\nSetup Google Comms\n");
    // TODO ! Create a Google Coms Failure boolean
    setupGoogleComs();
  #endif

  //*          SERIAL TELNET       *//
  #if B_SERIALTELNET==true
    Serial.printf("\nSetup Telnet Serial\n");
    BF_SERIALTELNET = !setupTelnet();
  #endif

  //*       SERIAL BLUETOOTH       *//
  #if B_BLE
    Serial.printf("\nSetup BLE Serial\n");
    BF_BLUETOOTH = !setupBluetooth();
  #endif

  //*          OTA SERVER      *//
  #if B_OTA == true
    Serial.printf("\nSetup OTA\n");
    // TODO ! Create a OTA Failure boolean
    setupOTA();
  #endif

  unsigned long setUpTimeEnd =  millis();
  DPRINTLN("Total setup time: " + String(float((setUpTimeEnd-setUpTime))/1000) + " s");

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
            // Updating last time for inactivity
            updateLastTime();

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
        #if B_SERIALPORT
          printSerial();
        #endif
        
        // Serial.printf("\n Free heap: %d", ESP.getFreeHeap()); // getSketchSize getFreeSketchSpace
        // Serial.printf("\n Skecth size: %d", ESP.getSketchSize());
        // Serial.printf("\n Vcc: %d", ESP.getVcc());

        // Google sheet data Sending  //
        #if B_GOOGLE_HTTPREQ
          // unsigned long tBeforeGoogle = millis();
          sendDataToGoogle();
          // unsigned long tAfterGoogle  = millis();
          // Serial.printf("%d ms to send data to Google",tAfterGoogle-tBeforeGoogle);
        #endif

        // Serial Telnet outputs  //
        #if B_SERIALTELNET == true
          // unsigned long tBeforeTelnet = millis();
          printSerialTelnet();
          // unsigned long tAfterTelnet  = millis();
          // Serial.printf("%d ms to send data thru Telnet",tAfterTelnet-tBeforeTelnet);
        #endif

        // OTA server   //
        #if B_OTA == true
          serverOTA.handleClient();
        #endif

        #if B_BLE == true
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
