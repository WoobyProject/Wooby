// #include "U8glib.h"
#include <U8g2lib.h>                 // by Oliver
#include "HX711.h"
// #include "Vcc.h"
#include <Wire.h>
#include <math.h>

#include "WoobyImage.h"
// #include "Filter.h"
#include "WoobyWiFi.h"
#include "Debugging.h"
#include <RunningAverage.h>

//************************//
//*      VERSION SEL     *//
//************************//

  #define MODEL 2
  #define TYPE 1

  // TYPE = 0 (PROTOTYPE)
  #if TYPE==0
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = false;
    bool B_DISPLAY_ANGLES = true;
    bool B_DISPLAY_ACCEL = true;
    bool B_INHIB_NEG_VALS = false;
    bool B_INACTIVITY_ACTIVE = false;
    bool B_HTTPREQ = true;
    bool B_SERIALPORT = true;
  #endif

// TYPE = 3 (PROTOTYPE-connectToWiFi)
  #if TYPE==3
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = false;
    bool B_DISPLAY_ANGLES = true;
    bool B_DISPLAY_ACCEL = true;
    bool B_INHIB_NEG_VALS = false;
    bool B_INACTIVITY_ACTIVE = false;
    bool B_HTTPREQ = false;
    bool B_SERIALPORT = true;
  #endif

  // TYPE = 1 (FINAL DELIVERY)
  #if TYPE==1
    bool B_ANGLE_ADJUSTMENT = true;
    bool B_VCC_MNG = true;
    bool B_LIMITED_ANGLES = true;
    bool B_DISPLAY_ANGLES = false;
    bool B_DISPLAY_ACCEL = false;
    bool B_INHIB_NEG_VALS = true;
    bool B_INACTIVITY_ACTIVE = true;
    bool B_HTTPREQ = true;
    bool B_SERIALPORT = true;
  #endif

//************************//
//*      SENSOR CONF     *//
//************************//
  #define DOUT 19     // For Arduino 6
  #define CLK  18     // For Arduino 5

  // For Arduino:
  // HX711 scale(DOUT, CLK);
  // For ESP:
  HX711 scale;

  int nMeasures = 7;
  int nMeasuresTare = 7;

  // Model choice
  #if MODEL == 1
    float calibrationFactor=42.00;
  #endif

  #if MODEL == 2
    float calibrationFactor=42.7461;
  #endif

  #if MODEL == 3
    // OLD BOOT LOADER
    float calibrationFactor=61.7977;
  #endif

  #if MODEL == 4
    float calibrationFactor=38.5299;
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
//*   LOAD SENSOR ADJ    *//
//************************//
  float TEMPREF = 26.0;

  float const P3 =   -1.2349e-06;
  float const P2 =    1.3114e-05;
  float const P1 =  -46.122436;
  float const P0 =  0.0;

  float const calib_theta_2 = -0.00014;
  float relativeVal_WU = 0;
  float realValue_WU_AngleAdj = 0;

  float tempCorrectionValue_WU = 0;
  float tempCorrectionValue = 0;

//************************//
//*  VCC MANAGEMENT CONF *//
//************************//

  const int PIN_VCC = 34;

  const float VCCMIN   = 0.0;         // Minimum expected Vcc level, in Volts.
  const float VCCMAX   = 7.3;         // Maximum expected Vcc level, in Volts.
  const float VGPIO_MES = 2.766;
  const float VCC_RATIO  = VCCMAX/VGPIO_MES; // Vcc/measured voltage on GPIO pin  (measured by multimeter)
  const float ADC_CORRECTION = VGPIO_MES/2520;

  float vccBits = 0;
  float vccGPIO = 0;
  float vccVolts = 0;
  float ratioVCCMAX = 0;

  // float myVcc, myVccFiltered;

  bool BF_VCCMNG = false;

  /*Vcc vcc(VCCCORR);
  Filter VccFilter(0.65, 10); // (Sampling time (depending on the loop execution time), tau for filter
  */

//************************//
//*   TARE BUTTON CONF   *//
//************************//

  #define TARE_BUTTON_PIN 27

  const int PIN_PUSH_BUTTON = 27; // TODO repetead

  unsigned long countTimeButton;

  int tareButtonStateN   = 0;
  int tareButtonStateN_1 = 0;
  int tareButtonFlank    = 0;

  unsigned long tStartTareButton = 0;
  unsigned long tEndTareButton = 0;

//************************//
//*      DISPLAY CONF    *//
//************************//

// For Arduino:
//  U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_DEV_0|U8G_I2C_OPT_NO_ACK|U8G_I2C_OPT_FAST); // Fast I2C / TWI
// For ESP32
  U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// For ESP32, replace 'setPrintPos' by 'setCursor'.
  int state = 0;
  char static aux[21] = "01234567890123456789";

  #define DISPLAY_WIDTH 128
  #define DISPLAY_HEIGHT 64

  bool bErrorDisplay = false;

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
//*  COMMUNICATION CONF  *//
//************************//

  unsigned long countForGoogleSend = 0;

//************************//
//*  WEIGHTING ALGO CONF *//
//************************//
  struct filterResult {
    float yk;
    int   bSync;
  };

  filterResult realValueFilterResult;

  float FILTERING_THR = 20;  // in grams
  float realValue;
  float realValue_1;
  float realValueFiltered;
  float realValueFiltered_1;
  int bSync;


  float realValue_WU = 0;

  float correctedValue = 0;
  RTC_DATA_ATTR float offset = 0;

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



  // TODO: This function may be redundant with readMPU()
  void readTemp(){
      Wire.beginTransmission(MPU_ADDR);
      Wire.write(0x41);
      Wire.endTransmission(false);
      Wire.requestFrom(MPU_ADDR,2,true);

      Tmp = Wire.read()<<8 | Wire.read(); // reading registers: 0x41 and 0x42
      myTmp = Tmp/340.00+36.53;
  }

  void readMPU(){

    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B);
    uint8_t errorEndTrans = Wire.endTransmission(false);

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

      /*
      myAx =    float(Ax)/16384;
      myAy = -1*float(Az)/16384;
      myAz =    float(Ay)/16384;
      */
      myAx =    float(Ax)/16384;
      myAy = -1*float(Ay)/16384;
      myAz = -1*float(Az)/16384;

      myGx =    float(Gx)/131;
      myGy =    float(Gy)/131;
      myGz =    float(Gz)/131;

      myTmp = Tmp/340.00+36.53;
    }
    else{
      Serial.println("ERROR: Reading MPU");
      BF_MPU = true;
    }
  }

  void angleCalc(){
    // Keep in mind that atan2() handles the zero div
      readMPU();
      phideg = (180/pi)*atan2(myAy,myAz);
      thetadeg =   (180/pi)*atan2(-1*myAx, sqrt(pow(myAz,2) + pow(myAy,2)));

  }

  void angleAdjustment(){

    if (B_ANGLE_ADJUSTMENT){
      angleCalc();
      if(!BF_MPU){
        realValue_WU_AngleAdj = relativeVal_WU/(1+calib_theta_2*pow(thetadeg, 2));
        return;
      }
    }
    realValue_WU_AngleAdj = relativeVal_WU;

  }

//*******************************//
//*      WEIGHTING ALGORITHM    *//
//*******************************//

void myTare(){
  DPRINTLN("TARE starting... ");
  unsigned long bTare = millis();
  scale.tare(nMeasuresTare);
  DPRINT("TARE time: "); DPRINT(float((millis()-bTare)/1000)); DPRINTLN(" s");

  readTemp();
  TEMPREF = myTmp;
  DPRINT("Reference Temp: "); DPRINT(TEMPREF); DPRINTLN(" C");
}

float correctionTemp(float beforeCorrectionValue){
  float deltaTemp = myTmp - TEMPREF;
  return ( beforeCorrectionValue / (P3*pow(deltaTemp,3) + P2*pow(deltaTemp,2) + P1*deltaTemp + P0) );
}

float correctionAlgo(float realValue){

  int realValueInt = int(realValue);
  float realValueDecim = (realValue - float(realValueInt)) ;
  float correctedValue = 0;

  // Around zero values deletion //
    if (realValue< MIN_GR_VALUE && realValue>-1*MIN_GR_VALUE){
      return correctedValue = 0.0;
    }

  // Round algorithm //
    if ( realValueDecim < 0.4) { correctedValue = long(realValueInt);}
    if ( realValueDecim >= 0.4 && realValueDecim <= 0.7) { correctedValue = long(realValueInt)+0.5 ; }
    if ( realValueDecim > 0.7) { correctedValue = long(realValueInt)+1; }

  return correctedValue;
}

filterResult filtering(float uk, float uk_1, float yk_1){
  // Definition of the coeffs for the filter
  float a =  0.3915;
  float b =  0.6085;

  filterResult myResult;
  if (abs(uk-uk_1) < FILTERING_THR) {
    // Filtering
    myResult.yk = a*uk_1 + b*yk_1;
    myResult.bSync = 0;
    }
  else{
    // Syncing
    myResult.yk = uk;
    myResult.bSync = 1;
  }

  return myResult;
}

//********************++++****//
//*   TARE BUTTON FUNCTIONS  *//
//*********************++++***//

void initTareButton(){

  //*         TARE BUTTON      *//
  pinMode(PIN_PUSH_BUTTON, INPUT);

  DPRINTLN("Initializing the tare button ... ");
  tareButtonStateN   = 0;
  tareButtonStateN_1 = 0;
  tareButtonFlank    = 0;
  tStartTareButton = 0;
  tEndTareButton = 0;
}

int updateTareButton(){
  delay(100);

  // Update
  tareButtonStateN_1 = tareButtonStateN;
  tareButtonStateN = digitalRead(TARE_BUTTON_PIN);
  tareButtonFlank = tareButtonStateN - tareButtonStateN_1;

  //if (tareButtonStateN)
  //  DPRINTLN("Tare button pushed! ");

  switch (tareButtonFlank){
    case   1: DPRINTLN("Up flank!");
              tStartTareButton = millis();
              return -1;
              break;
    case  -1: DPRINTLN("Down flank!");
              tEndTareButton = millis();
              // Serial.print("Time:");
              // Serial.println(tEndTareButton-tStartTareButton);
              return (tEndTareButton-tStartTareButton);
              break;
    default:  return -1;
              break;
  }
}

/*
void tareButtonFunction() // TODO: verify if this is ok (and/or used)
{
  int Push_button_state = digitalRead(PIN_PUSH_BUTTON);
  if ( Push_button_state == HIGH )
  {
    myTare();
  }
}
*/

void tareButtonAction()
{
  int timeButton = updateTareButton();
  if (timeButton>200){
    DPRINTLN("Time tare button: ");
    DPRINTLN(timeButton);
    myTare();
  }
}

//************************//
//* VCC MANAGEMENT FUNCS *//
//************************//


void readVcc(){

  // Reading pin
  vccBits = float(analogRead(PIN_VCC));


  // Calulation for displaying
  vccGPIO = vccBits*ADC_CORRECTION;
  vccVolts = vccGPIO*VCC_RATIO;
  ratioVCCMAX = min((vccVolts/VCCMAX), float(1.0));


  Serial.printf("\nVoltage read (bits): %f", vccBits);
  Serial.printf("\nReal GPIO voltage (V): %f",   vccGPIO);
  Serial.printf("\nVCC_RATIO(V): %f",   VCC_RATIO);
  Serial.printf("\nImage to Vcc (V): %f ",   vccVolts);
  Serial.printf("\nRatio to Vcc (%): %d \n", int(100*ratioVCCMAX));

   /* For Arduino:
   myVcc = vcc.Read_Volts();
   // int deltaOFFSETVcc = correctionVcc(myVcc);
   myVccFiltered = VccFilter.update(myVcc);

   ratioVCCMAX = min(myVccFiltered/VCCMAX, 1.0);
   */

}

void setupVccMgnt(){
  // For Arduino:
  // myVcc = vcc.Read_Volts();
  // VccFilter.init(myVcc);

  analogReadResolution(12);
  analogSetWidth(12);
  analogSetPinAttenuation(PIN_VCC,ADC_11db); // Sets the input attenuation, default is ADC_11db, range is ADC_0db, ADC_2_5db, ADC_6db, ADC_11db
                                        // ADC_0db provides no attenuation so IN/OUT = 1 / 1 an input of 3 volts remains at 3 volts before ADC measurement
                                        // ADC_2_5db provides an attenuation so that IN/OUT = 1 / 1.34 an input of 3 volts is reduced to 2.238 volts before ADC measurement
                                        // ADC_6db provides an attenuation so that IN/OUT = 1 / 2 an input of 3 volts is reduced to 1.500 volts before ADC measurement
                                        // ADC_11db provides an attenuation so that IN/OUT = 1 / 3.6 an input of 3 volts is reduced to 0.833 volts before ADC measurement

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
      u8g.setFlipMode(1);


  // Set up of the default font
    u8g.setFont(u8g2_font_6x10_tf);
    // u8g.setFont(u8g_font_9x18);
    // u8g.setFont(u8g2_font_osb18_tf);

 // Other display set-ups
    u8g.setFontRefHeightExtendedText();
    // For Arduino: u8g.setDefaultForegroundColor();
    u8g.setFontPosTop();

    bErrorDisplay = false;
  }
  catch(int e){
    Serial.println("Not possible to activate the display");
    bErrorDisplay = true;
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
      u8g.setFont(u8g_font_6x10);
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

      u8g.setFont(u8g_font_6x10);
      u8g.drawStr( 60, 35, "&");

      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 15, 55, "MEDAIR");
   }while(u8g.nextPage());

  Serial.println("Waiting 1 sec...");
  delay(1000);
  Serial.println("");

}

void clockShoot(int currentTime, int finalTime) {

  int X0 = DISPLAY_WIDTH/2;
  int Y0 = DISPLAY_HEIGHT/2;
  int R = int(DISPLAY_HEIGHT*0.5*0.5);
  int GAP = R*0.25;

  float N = float(currentTime)/float(finalTime);
  int X = X0 + int((R-GAP)*sin(N*2*3.1416)) ;
  int Y = Y0 - int((R-GAP)*cos(N*2*3.1416)) ;

  u8g.drawCircle(X0, Y0, R);
  u8g.drawCircle(X0, Y0, R-2);
  u8g.drawLine(X0, Y0, X, Y);

  u8g.setCursor(15, 55) ;
  u8g.print(int((finalTime-currentTime)/1000)+1, 1);

}

void wakingUpDisplay(){
  // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do{
    u8g.setFont(u8g2_font_helvR08_tf); //u8g_font_6x10
    u8g.drawStr( 45, 10, "Woooooby!");
    u8g.setFont(u8g2_font_helvR14_tf);
    u8g.drawStr( 20, 20, "Waking up");
  }while(u8g.nextPage());
  delay(1000);
}

void sleepingDisplay(){
  // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do{
    u8g.setFont(u8g2_font_artossans8_8r); //u8g_font_6x10
    u8g.drawStr( 55, 10, "zzz");
    u8g.setFont(u8g2_font_helvR14_tf);
    u8g.drawStr( 30, 25, "Going to");
    u8g.setFont(u8g2_font_helvR14_tf);
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

void manage_wakeup_reason(){
  if (esp_sleep_get_wakeup_cause()==2){
    Serial.println("Wakeup caused by external signal using RTC_IO");
  }
  else{
    Serial.println("Wakeup was not caused by deep sleep");
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
//* HTTP REQUEST FUNCTIONS *//
//**************************//

void setupGoogleComs(){
  if (B_HTTPREQ){
  //*       GOOGLE CONNECTION        *//
     clientForGoogle.setCACert(root_ca);
  //*         WIFI CONNECTION        *//
     setupWiFi();
     // Checking WiFi connection //
     BF_WIFI = !checkWiFiConnection();
  }
}

void hashJSON(char* data, unsigned len) {
  // Hash encryption of the JSON
  sha.resetHMAC(key, sizeof(key));
  sha.update(data, len);
  sha.finalizeHMAC(key, sizeof(key), hmacResult, sizeof(hmacResult));
  Serial.println("DataSize :" + String(len));
  Serial.println(data);
  Serial.println("HashSize :" + String(sha.hashSize( )));
  Serial.println("BlockSize:" + String(sha.blockSize()));
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
  if (!B_HTTPREQ){
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

//***************************//
//* SERIAL COMMS FUNCTIONS  *//
//***************************//

void printSerial()
{
  if (!B_SERIALPORT)
    return;

  Serial.print("WS");

  Serial.print("tBeforeMeasure");               Serial.print(":");
  Serial.print(tBeforeMeasure);                 Serial.print(",\t");
  Serial.print("tAfterMeasure");                Serial.print(":");
  Serial.print(tAfterMeasure);                  Serial.print(",\t");
  Serial.print("tAfterAlgo");                   Serial.print(":");
  Serial.print(tAfterAlgo);                     Serial.print(",\t");


  Serial.print("realValue_WU");                 Serial.print(":");
  Serial.print(realValue_WU);                   Serial.print(",\t");
  Serial.print("OFFSET");                       Serial.print(":");
  Serial.print(offset);                         Serial.print(",\t");
  Serial.printf("calibrationFactor:%f,\t", calibrationFactor);

  Serial.print("relativeVal_WU");               Serial.print(":");
  Serial.print(relativeVal_WU);                 Serial.print(",\t");
  Serial.print("realValue_WU_AngleAdj");        Serial.print(":");
  Serial.print(realValue_WU_AngleAdj);          Serial.print(",\t");
  Serial.print("realValue");                    Serial.print(":");
  Serial.print(realValue, 5);                   Serial.print(",\t");
  Serial.print("realValueFiltered");            Serial.print(":");
  Serial.print(realValueFiltered, 5);           Serial.print(",\t");
  Serial.print("correctedValueFiltered");       Serial.print(":");
  Serial.print(correctedValueFiltered, 5);      Serial.print(",\t");


  Serial.print("myAx");                     Serial.print(":");
  Serial.print(myAx);                       Serial.print(",\t");
  Serial.print("myAy");                     Serial.print(":");
  Serial.print(myAy);                       Serial.print(",\t");
  Serial.print("myAz");                     Serial.print(":");
  Serial.print(myAz);                       Serial.print(",\t");
  Serial.print("myGx");                     Serial.print(":");
  Serial.print(myGx);                       Serial.print(",\t");
  Serial.print("myGy");                     Serial.print(":");
  Serial.print(myGy);                       Serial.print(",\t");
  Serial.print("myGz");                     Serial.print(":");
  Serial.print(myGz);                       Serial.print(",\t");

  Serial.print("thetadeg");                     Serial.print(":");
  Serial.print(thetadeg);                       Serial.print(",\t");
  Serial.print("phideg");                       Serial.print(":");
  Serial.print(phideg);                         Serial.print(",\t");

  Serial.print("myTmp");                        Serial.print(":");
  Serial.print(myTmp);                          Serial.print(",\t");

  Serial.printf("BF_MPU:%d\t",BF_MPU);


  Serial.printf("VCC_RATIO:%f\t",VCC_RATIO);
  Serial.printf("ADC_CORRECTION:%f\t",ADC_CORRECTION);
  Serial.printf("vccBits:%f\t",vccBits);
  Serial.printf("vccGPIO:%f\t",vccGPIO);
  Serial.printf("vccVolts:%f\t",vccVolts);

  Serial.printf("bSync:%d\t",bSync);

  /*
  Serial.print("tareButtonFlank");              Serial.print(":");
  Serial.print(tareButtonFlank);                Serial.print(",\t");
  */



  Serial.println("");
}

void printSerialOld()
{

  Serial.print(tAfterAlgo);                     Serial.print(",\t");
  Serial.print(realValue, 4);                   Serial.print(",\t");
  Serial.print(correctedValue, 4);              Serial.print(",\t");
  Serial.print(tBeforeMeasure);                 Serial.print(",\t");
  Serial.print(tAfterMeasure);                  Serial.print(",\t");
  Serial.print(realValueFiltered, 4);           Serial.print(",\t");
  Serial.print(correctedValueFiltered, 4);      Serial.print(",\t");
  Serial.print(bSync);                          Serial.print(",\t");
  Serial.print(calibrationFactor,4);           Serial.print(",\t");
  //Serial.print(valLue_WU/realvalLue,4);Serial.print(",\t");
  Serial.print(offset, 4);                      Serial.print(",\t");
  Serial.print(realValue_WU);                   Serial.print(",\t");
  Serial.print(bInactive);                      Serial.print(",\t");
  Serial.print(lastTimeActivity);               Serial.print(",\t");
  Serial.print(vccVolts);                       Serial.print(",\t");
  // Serial.print((float)scale.get_Vcc_offset(), 4);Serial.print(",\t");

  Serial.print(myAx);                           Serial.print(",\t");
  Serial.print(myAy);                           Serial.print(",\t");
  Serial.print(myAz);                           Serial.print(",\t");
  Serial.print(myGx);                           Serial.print(",\t");
  Serial.print(myGy);                           Serial.print(",\t");
  Serial.print(myGz);                           Serial.print(",\t");

  Serial.print(thetadeg);                       Serial.print(",\t");
  Serial.print(phideg);                         Serial.print(",\t");

  Serial.print(myTmp);                          Serial.print(",\t");
  Serial.print(TEMPREF);                        Serial.print(",\t");
  Serial.print(tempCorrectionValue);            Serial.print(",\t");

  Serial.println("");
}

//*************************//
//*    MACRO FUNCTIONS    *//
//*************************//

void setUpWeightAlgorithm(){
    realValue_1 = 0;
    realValueFiltered = 0;
    realValueFiltered_1 = 0;
    bSync = false;
}

void getWoobyWeight(){

    // Raw weighting //
    tBeforeMeasure = millis();
    realValue_WU = scale.read_average(nMeasures);
    tAfterMeasure = millis();

    offset = (float)scale.get_offset();
    relativeVal_WU = realValue_WU - offset;

    // Angles correction //
    angleAdjustment();

    // Conversion to grams //
    realValue = (realValue_WU_AngleAdj)/scale.get_scale();
    correctedValue = correctionAlgo(realValue); // NOT USED!!!!!

    // Filtering  //

      // Filtering for the real value //
      realValueFilterResult = filtering(realValue, realValue_1, realValueFiltered_1);
      bSync = realValueFilterResult.bSync;
      realValueFiltered = realValueFilterResult.yk;

      // Updating for filtering
      realValueFiltered_1 = realValueFiltered;
      realValue_1 = realValue;

    // Final correction  //
    correctedValueFiltered = correctionAlgo(realValueFiltered);

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

            u8g.setFont(u8g_font_6x10);
            u8g.setCursor(23, 45) ; // (Horiz, Vert)
            u8g.print("Negative values");

        } while(u8g.nextPage());
  }
  else if ((abs(thetadeg) > MAX_THETA_VALUE || abs(phideg) > MAX_PHI_VALUE ) && (B_LIMITED_ANGLES)){ // Verification of the maximum allowed angles
       do {
            u8g.setFont(u8g2_font_osb18_tf);
            u8g.setCursor(17, 30) ; // (Horiz, Vert)
            u8g.print(" OUPS !");

            u8g.setFont(u8g_font_6x10);
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
          u8g.setFont(u8g_font_6x10);
          u8g.setFontPosBottom();
          u8g.setCursor(5, DISPLAY_HEIGHT-2);
          BF_MPU? u8g.print("???"): u8g.print(int(thetadeg), 10);


          u8g.setFont(u8g_font_6x10);
          u8g.setFontPosBottom();
          u8g.setCursor(55, DISPLAY_HEIGHT-2);
          BF_MPU? u8g.print("???"): u8g.print(String(int(myTmp)) + "("+ String(int(TEMPREF)) + ")");

          u8g.setFont(u8g_font_6x10);
          u8g.setFontPosBottom();
          u8g.setCursor(100, DISPLAY_HEIGHT-2);
          BF_MPU? u8g.print("???"): u8g.print(int(phideg), 10);
        }

        if (B_DISPLAY_ACCEL){
          u8g.setFont(u8g_font_6x10);

          u8g.setCursor(4, 24);
          BF_MPU? u8g.print("???"):u8g.print(roundf(myAx*100.0)/100.0);

          u8g.setCursor(4, 31);
          BF_MPU? u8g.print("???"):u8g.print(roundf(myAy*100.0)/100.0);

          u8g.setCursor(4, 38);
          BF_MPU? u8g.print("???"):u8g.print(roundf(myAz*100.0)/100.0);

        }

        // Display batterie levels //

          u8g.setFont(u8g_font_6x10);
          u8g.setFontPosTop();
          u8g.setCursor(100, 12) ; // (Horiz, Vert)
          BF_VCCMNG ? u8g.print("??") : u8g.print(int(100*ratioVCCMAX));


          u8g.setFont(u8g_font_6x10);
          u8g.setFontPosTop();
          u8g.setCursor(120, 12);
          u8g.print("%");

          u8g.drawLine(100,   2,    100+22, 2); // (Horiz, Vert)
          u8g.drawLine(100,   2+7,  100+22, 2+7);
          u8g.drawLine(100,   2,    100,    2+7);
          u8g.drawLine(100+22,2,    100+22, 2+7);

          u8g.drawBox(100+22+1,2+2,2, 7-4+1);
          u8g.drawBox(100+2,2+2,int((22-4+1)*ratioVCCMAX),7-4+1); // (Horiz, Vert, Width, Height)

        // Display connections //
          u8g.setFont(u8g2_font_open_iconic_www_1x_t);
          u8g.drawStr( 4, 2, "Q");
          if (!B_HTTPREQ)
            u8g.drawLine(2,  11,  11, 2);

          u8g.setFont(u8g_font_6x10);
          u8g.drawStr( 20, 3, "S");
          if (!B_SERIALPORT)
            u8g.drawLine(17,  11,  26, 2);



    } while(u8g.nextPage());
  }

  if (B_INACTIVITY_ACTIVE){
    inactivityCheck();
    handleActionInactivity();
  }
}

//************************//
//*       SET UP        *//
//************************//

void setup(void) {

  Serial.begin(115200);
  unsigned long setUpTime =  millis();


  DPRINTLN("If I do tan of something/0");
  DPRINTLN(atan2(1,0));

  DPRINTLN("If I do tan of 0/0");
  DPRINTLN(atan2(0,0));

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

  //*            FILTERING            *//
  setUpWeightAlgorithm();

  //*          INACTIVITY          *//
  setUpInactivity();

  //*          TARE BUTTON         *//
  initTareButton();

  //*          AUTO TARE         *//
  if(wakeupReason!=2){
      myTare();
  }

  //*          VCC MANAGEMENT        *//
  setupVccMgnt();

  //*          GOOGLE COMS        *//
  setupGoogleComs();

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
            displayImage(logoWooby);
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
            tareButtonAction();

            //   //
            readVcc();

            // Weighting //
            getWoobyWeight();

            // GyroAcc adjustement  //

            // Temperature algorithm // TODO: create a function
            tempCorrectionValue_WU = (P1*(myTmp-TEMPREF)+P0); //
            tempCorrectionValue = (tempCorrectionValue_WU)/scale.get_scale();

            // Serial monitor outputs  //
            printSerial();

            // Google sheet data Sending  //
            sendDataToGoogle();

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
