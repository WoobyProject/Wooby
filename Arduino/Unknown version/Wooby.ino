#include "U8glib.h"
#include "HX711.h"
#include "Vcc.h"
#include <Wire.h>
#include <math.h>
#include "Filter.h"

//***********************//
//*     VERSION SEL    *//
//***********************//

  #define MODEL 3
  #define TYPE 0
  // TYPE = 0 (PROTOTYPE)
  // TYPE = 1 (FINAL DELIVERY)
  
//***********************//
//*     SENSOR CONF    *//
//***********************//

  #define DOUT 6
  #define CLK 5
  #define TARE_BUTTON 7
  
  HX711 scale(DOUT, CLK);
  int nMeasures = 7;
  int nMeasuresTare = 30;
  
  // Model choice
  #if MODEL == 1 
    float calibration_factor=41.9541;
  #endif

  #if MODEL == 2  
    // OLD BOOT LOADER
    float calibration_factor=-42.5012;
  #endif

  #if MODEL == 3  
    // OLD BOOT LOADER
    float calibration_factor=-61.7977; 
  #endif
  
  #if MODEL == 4
    float calibration_factor= 38.5299;
  #endif
  
  int gain = 64;  // Reading values with 64 bits (could be 128 too)

  float MAX_GR_VALUE = 10000; // in gr 
  float MIN_GR_VALUE = 5;    // in gr
  
  float correctedValueFiltered = 0;
  float displayFinalValue = 0;
  float displayFinalValue_1 = 0;

//***********************//
//*  SENSOR CONF TEMP   *//
//***********************//

float TEMPREF = 26.0;

float const P3 =   -1.2349e-06;
float const P2 =    1.3114e-05;
float const P1 =  0.0019 ;
float const P0 =  1.000;

//***********************//
//* VCC MANAGEMENT CONF *//
//***********************//

  const float VCCMIN   = 0.0;           // Minimum expected Vcc level, in Volts.
  const float VCCMAX   = 5.0;           // Maximum expected Vcc level, in Volts.
  const float VCCCORR  = 5.0/5.01;      // Measured Vcc by multimeter divided by reported Vcc

  float myVcc, myVccFiltered, ratioVCCMAX;
  Vcc vcc(VCCCORR);
  Filter VccFilter(0.65, 10); // (Sampling time (depending on the loop execution time), tau for filter 
  
//***********************//
//*     DISPLAY CONF    *//
//***********************//

  //lolo: lib la plus rapide
  //U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_DEV_0|U8G_I2C_OPT_NO_ACK|U8G_I2C_OPT_FAST);  // Fast I2C / TWI 
  
  //U8GLIB_SSD1306_128X64 u8g(13, 11, 10, 9, 8);  // SW SPI Com: SCK = 13, MOSI = 11, CS = 10, A0 = 9
  //U8GLIB_SSD1306_128X64 u8g(4, 5, 6, 7);  // SW SPI Com: SCK = 4, MOSI = 5, CS = 6, A0 = 7 (new white HalTec OLED)
  //U8GLIB_SSD1306_128X64 u8g(10, 9);   // HW SPI Com: CS = 10, A0 = 9 (Hardware Pins are  SCK = 13 and MOSI = 11)
  //U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_NONE|U8G_I2C_OPT_DEV_0);  // I2C / TWI 
  U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_DEV_0|U8G_I2C_OPT_NO_ACK|U8G_I2C_OPT_FAST); // Fast I2C / TWI 
  //U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_NO_ACK);  // Display which does not send AC


  //U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_NONE|U8G_I2C_OPT_DEV_0);  // I2C / TWI 
  //U8GLIB_SSD1306_128X64 u8g(10, 9);    // HW SPI Com: CS = 10, A0 = 9 (Hardware Pins are  SCK = 13 and MOSI = 11)
  int state = 0;
  char static aux[20] = "01234abcde56789ABCDE";
  
  #define DISPLAY_WIDTH 128
  #define DISPLAY_HEIGHT 64

  const unsigned char logoWooby [] U8G_PROGMEM = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0x0F, 0x00, 0xC0, 0x03, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x1F, 
        0x00, 0xE0, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xF0, 0x1F, 0x00, 0xF0, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0x3F, 0x00, 0xF8, 0x1F, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0x3F, 
        0x7E, 0xF8, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xF8, 0x3F, 0xFF, 0xFC, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0x3F, 0xFF, 0xFC, 0x1F, 0x00, 
        0x00, 0x3C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0xBF, 
        0xFF, 0xFD, 0x1F, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xF8, 0xBF, 0xFF, 0xFD, 0x1F, 0x00, 0x00, 0x7E, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0xBF, 0xFF, 0xFD, 0x1F, 0x00, 
        0x00, 0xFE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0xBF, 
        0xFF, 0xFD, 0x1F, 0x00, 0x00, 0xFE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xF0, 0x9F, 0xFF, 0xFB, 0x0F, 0x00, 0x00, 0xFE, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x9F, 0xFF, 0xFB, 0x0F, 0x00, 
        0x00, 0xFE, 0x78, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xDF, 
        0xFF, 0xFB, 0xC7, 0x03, 0x78, 0xFC, 0xFD, 0xF1, 0x01, 0x06, 0x00, 0x00, 
        0x00, 0x00, 0xE0, 0xDF, 0xFF, 0xFB, 0xF7, 0x0F, 0xFE, 0xFD, 0xFF, 0xF9, 
        0x81, 0x1F, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xDF, 0xFF, 0xFF, 0xFB, 0x1F, 
        0xFF, 0xFF, 0xFF, 0xFB, 0xC3, 0x1F, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xCF, 
        0xFF, 0xFF, 0xFF, 0x9F, 0xFF, 0xFF, 0xFF, 0xFB, 0xE3, 0x1F, 0x00, 0x00, 
        0x00, 0x00, 0xC0, 0xCF, 0xFF, 0xFF, 0xFF, 0xBF, 0xFF, 0xFF, 0xFF, 0xF7, 
        0xE3, 0x1F, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xCF, 0xFF, 0xFF, 0xFF, 0xFF, 
        0xFF, 0xFF, 0xFF, 0xF7, 0xF7, 0x0F, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xCF, 
        0xF7, 0xFF, 0x7F, 0xFE, 0xCF, 0xFF, 0xE7, 0xF7, 0xF7, 0x0F, 0x00, 0x00, 
        0x00, 0x00, 0xC0, 0xEF, 0xE3, 0xFF, 0x3F, 0xFE, 0x87, 0xFF, 0xE3, 0xF7, 
        0xFF, 0x07, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xEF, 0xE3, 0xFF, 0x3F, 0xFC, 
        0x87, 0xFF, 0xE3, 0xE7, 0xFF, 0x03, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xFF, 
        0xC1, 0xFF, 0x3F, 0xFC, 0x87, 0xFF, 0xE3, 0xE7, 0xFF, 0x01, 0x00, 0x00, 
        0x00, 0x00, 0xC0, 0xFF, 0xC1, 0xFF, 0x3F, 0xFE, 0x8F, 0xFF, 0xE3, 0xE7, 
        0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xFF, 0xC1, 0xFF, 0x7F, 0xFF, 
        0xCF, 0xFF, 0xF3, 0xE7, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xFF, 
        0xC1, 0xFF, 0xFF, 0xBF, 0xFF, 0xFF, 0xF3, 0xF7, 0x7F, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xE0, 0xFF, 0x81, 0xFF, 0xFF, 0xBF, 0xFF, 0xFF, 0xFF, 0xF7, 
        0x3F, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xFF, 0x81, 0xFF, 0xFB, 0x1F, 
        0xFF, 0xFB, 0xFF, 0xF7, 0x3F, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xFF, 
        0x81, 0xFF, 0xFB, 0x0F, 0xFE, 0xFB, 0xFF, 0xF3, 0x1F, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xC0, 0xFF, 0x81, 0xFF, 0xE3, 0x07, 0xFC, 0xF8, 0xFF, 0xFB, 
        0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xFF, 0x81, 0xFF, 0x03, 0x00, 
        0x00, 0xF8, 0xFF, 0xF9, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xFF, 
        0x00, 0xFF, 0x01, 0x00, 0x00, 0xF8, 0xFF, 0xFD, 0x07, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xC0, 0xFF, 0x00, 0xFF, 0x3F, 0x00, 0x00, 0xF8, 0x7E, 0xFE, 
        0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x7F, 0x00, 0xFE, 0x7E, 0x00, 
        0x00, 0x70, 0x00, 0xFE, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3F, 
        0x00, 0x3C, 0xFE, 0x01, 0x00, 0x00, 0x00, 0xFF, 0x01, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFE, 0x03, 0x00, 0x00, 0x80, 0xFF, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFE, 0x0F, 
        0x00, 0x00, 0xE0, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xFE, 0x1F, 0x00, 0x00, 0xF0, 0x1F, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFC, 0xFF, 0x00, 0x00, 0xFC, 0x0F, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0xFF, 
        0x07, 0xC0, 0xFF, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0xF0, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xFF, 0xFF, 0xFF, 0x7F, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFC, 
        0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0xE0, 0xFF, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x01, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, };

//***********************//
//*   INACTIVITY CONF   *//
//***********************//

  const float MAX_INACTIVITY_TIME = 100000; // in milliseconds 
  const float INACTIVE_THR  = 5.0;
  bool bInactive = false;
  unsigned long lastTimeActivity = 0;
  const byte interruptPin = 2;

//***********************//
//*    GYROSCOPE CONF   *//
//***********************//
  const int MPU_ADDR=0x68; 
  const float pi = 3.1416;
  int16_t Ax,Ay,Az,Tmp,Gx,Gy,Gz;
  float myAx, myAy, myAz, myTmp, myGyroX, myGyroY, myGyroZ;
  float theta, phi, thetadeg, phideg ;
  
  const float MAX_THETA_VALUE = 10;
  const float MAX_PHI_VALUE = 10;

//***********************//
//* FILTERING FUNCTIONS *//
//***********************//
    // Filter 
    struct filterResult {
      float yk;
      int   bSync;
    };
    
    filterResult realValueFilterResult;

    float realValue;
    float realValue_1;
    float realValueFiltered;
    float realValueFiltered_1;
    int bSync;
    int bSync_corr = 0;

//*******************************//
//*      WEIGHTING ALGORITHM    *//
//*******************************//

  void myTare(){
      Serial.print("Before TARE"); Serial.println(millis());
      long tareWU = scale.tare(nMeasuresTare); 
      Serial.print("After TARE"); Serial.println(millis());
      
      float tareGR = tareWU/scale.get_scale();
      TEMPREF = myTmp;

      Serial.print("Reference Temp:"); Serial.println(TEMPREF);
  }

    float correctionTemp(float beforeCorrectionValue){
      float deltaTemp = myTmp - TEMPREF;
      return ( beforeCorrectionValue / (P3*pow(deltaTemp,3) + P2*pow(deltaTemp,2) + P1*deltaTemp + P0) );
    }
       
    float correctionAlgo(float realValue){
      
      int realValueInt = int(realValue);
      float realValueDecim = (realValue - float(realValueInt)) ;
      float correctedValue;
      
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
       float a =  0.3915;
       float b = 0.6085;
        
      filterResult myResult;
      if (abs(uk-uk_1) < 5) {
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



//***********************//
//*  DISPLAY FUNCTIONS  *//
//***********************//
   
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
    u8g.setFont(u8g_font_osb18);
    
    do {
        u8g.setFont(u8g_font_6x10);
        u8g.drawStr( 30, 15, "Powered by");
        u8g.setFont(u8g_font_osb18);
        u8g.drawStr( 10, 40, "Humanity");
        u8g.setFont(u8g_font_osb18);
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
      u8g.setFont(u8g_font_osb18);
    
    // Display loop
     do {
        u8g.setFont(u8g_font_osb18);
        u8g.drawStr( 15, 25, "AIRBUS");
        
        u8g.setFont(u8g_font_6x10);
        u8g.drawStr( 60, 35, "&");
        
        u8g.setFont(u8g_font_osb18);
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
    
    u8g.setPrintPos(15, 55) ;
    u8g.print(int((finalTime-currentTime)/1000)+1, 1);

  }
  
  void clockDisplay(){
    
    int totalTimeLapse = 4000; // in milliseconds 
    unsigned long entryTime = millis();
    
    // Display loop
     do {
      // Set up the display
      u8g.firstPage();
      u8g.setFont(u8g_font_osb18);
      do {
       clockShoot((millis()-entryTime), totalTimeLapse) ;
      }while( u8g.nextPage()); 
          
     
     }while( (millis()-entryTime) <= totalTimeLapse); 

     unsigned long exitTime = millis();
     Serial.print("Entry time (s):"); Serial.println(float(entryTime/1000));
     Serial.print("Exit time (s):"); Serial.println(float(exitTime/1000));
  }

  
//***************************//
//*  INACTIVITY FUNCTIONS   *//
//***************************//

void inactivityCheck () {

  // Checking activity
    if (abs(displayFinalValue - displayFinalValue_1 ) > INACTIVE_THR ){
          Serial.print("Active: ");Serial.print(bInactive);
          lastTimeActivity =  millis();
          if (bInactive){
            // Waking the Arduino up
             
             
            // Waking the screen up
            u8g.sleepOff();
            bInactive =  false;
            }
    }

  // Checking inactivity 
    if ((millis() - lastTimeActivity) > MAX_INACTIVITY_TIME){
          Serial.println("Inactive");
          bInactive = true;

          // Putting the screen in sleep mode
          u8g.sleepOn();

          // Putting the Arduino in sleep mode
          /*set_sleep_mode(SLEEP_MODE_PWR_DOWN);
          sleep_enable();
          sleep_cpu();*/
    }

                
}

void wakeUp (void){
  bInactive = false;
  lastTimeActivity =  millis();
  u8g.sleepOff();
}

//************************//
//* GYRO/ACCEL FUNCTIONS *//
//************************//

struct GSread{
  int16_t Ax, Ay, Az, T, Gx, Gy, Gz;
};

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

void readAccel(){

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR,14,true); 
  
  Ax = Wire.read()<<8 | Wire.read(); // reading registers: 0x3B and 0x3C
  Ay = Wire.read()<<8 | Wire.read(); // reading registers: 0x3D  and 0x3E
  Az = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F  and 0x40 
  Tmp = Wire.read()<<8 | Wire.read(); // reading registers: 0x41 and 0x42
  Gx = Wire.read()<<8 | Wire.read(); // reading registers: 0x43 and 0x44 
  Gy = Wire.read()<<8 | Wire.read(); // reading registers: 0x45 and 0x46 
  Gz = Wire.read()<<8 | Wire.read(); // reading registers: 0x47  and 0x48 

  myAx = float(Ax)/16384;
  myAy = -1*float(Az)/16384;
  myAz = float(Ay)/16384;
  
  myGyroX = float(Gx)/131;
  myGyroY = float(Gy)/131;
  myGyroZ = float(Gz)/131;

  myTmp = Tmp/340.00+36.53;

}

void angleCalc (){
    readAccel();

    phi = atan2(myAy,myAz);
    theta =  atan2(-1*myAx, sqrt(pow(myAz,2) + pow(myAy,2)));
    phideg = (180/pi)*phi;
    thetadeg =   (180/pi)*theta;

}

//***********************//
//*       SET UP        *//
//***********************//

void setup(void) {

  Serial.begin(115200);
  Serial.println("peseBebe v1");
  Serial.println("Initializing the scale");
  
  
  //*       SET UP  WEIGHT SENSOR       *//
  
    scale.begin(DOUT, CLK);
    scale.set_gain(gain);
    scale.set_scale(calibration_factor); 


  //*         ACCELEROMETER           *//
    setupMPU();
    readAccel();
  
  //*            AUTO TARE             *//  
  
    myTare();

  //*            FILTERING            *//  
    
    realValue_1 = 0;
    realValueFiltered = 0;
    realValueFiltered_1 = 0;
    bSync = false;
    
    float yk_1 = 0;
    float uk_1 = 0;
    float yk = 0;
    
  //*          SCREEN SETUP          *//  
      // Flip screen, if required
        u8g.setRot180();
        
      // Set up of the font
        u8g.setFont(u8g_font_6x10);
        // u8g.setFont(u8g_font_9x18);
        // u8g.setFont(u8g_font_osb18);
        
     // Other display set-ups
        u8g.setFontRefHeightExtendedText();
        u8g.setDefaultForegroundColor();
        u8g.setFontPosTop();

  //*          INACTIVITY          *//
    Serial.print("CLOCK DIVISION:"); Serial.println(CLKPR);         
    lastTimeActivity =  millis();
    pinMode(interruptPin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(interruptPin), wakeUp, CHANGE);

 //*          VCC MANAGEMENT        *//   
    myVcc = vcc.Read_Volts(); 
    VccFilter.init(myVcc);
    
  #if defined(ARDUINO)
    pinMode(13, OUTPUT);           
    digitalWrite(13, HIGH);  
  #endif

}

//***********************//
//*        LOOP         *//
//***********************//

  unsigned long timeAfterAlgo;
  
  void loop(void) {
    
  //  Serial.println("State: " + String(state));
  
    
    unsigned long beforeMeasure = 0;
    unsigned long afterMeasure = 0;
       

    char arrayMeasure[8];
    
    
   //  Vcc measurement //
      myVcc = vcc.Read_Volts();
      // int deltaOFFSETVcc = correctionVcc(myVcc);
      myVccFiltered = VccFilter.update(myVcc);
      ratioVCCMAX = min(myVccFiltered/VCCMAX, 1.0);
                

    //********************************//
    //*  READING OF SERIAL ENTRIES   *//
    //********************************//
      if(Serial.available())
      {
        char temp = Serial.read();
        switch(temp){
        case '+': calibration_factor += 1;
                  scale.set_scale(calibration_factor);
                  break;
        case '-': calibration_factor -= 1;
                  scale.set_scale(calibration_factor);
                  break;
        case 'a': calibration_factor += 0.1;
                  scale.set_scale(calibration_factor);
                  break;
        case 'z': calibration_factor -= 0.1;
                  scale.set_scale(calibration_factor);
                  break;
        case 't': myTare();
    
                  break;
        default:
                  break;
        }
                  
      }
      
  
    //u8g_prepare();
    switch (state) {
      case 0:  // clockDisplay();
               // poweredByDisplay();
               state++;
      break;
      case 1:
              // initialMessage();
              // sponsorsDisplay();
              state++;
      break;
      
      case 2:
              displayImage(logoWooby);
              // logoWoobyDisplay();
              state++;
              
              // Displaying and weighting is about to begin
              Serial.println("DATA START");
              
      break;
      case 3:                
             
              
              // Display characteristics
                // u8g.setFont(u8g_font_9x18);
                // u8g.setFont(u8g_font_osb18); 
                // u8g.setFontPosTop();
              // Set up the display
                u8g.firstPage();
                
              // Main display loop

              // Weighting //

                beforeMeasure = millis();
                float realValue_WU = scale.read_average(nMeasures);
                float realValue = (realValue_WU-scale.get_offset()-scale.get_Vcc_offset())/scale.get_scale() ;  // same as scale.get_units(nMeasures)
                afterMeasure = millis();
                
                float correctedValue = correctionAlgo(realValue);

              // GyroAcc adjustement  //
              
                angleCalc();

              // Temperature algorithm // 
                float correctedTempValue = correctionTemp(realValue);
      
              // Filtering  //
              
                // Filtering for the real value //
                  realValueFilterResult = filtering(realValue, realValue_1, realValueFiltered_1);
                  bSync = realValueFilterResult.bSync;
                  realValueFiltered = realValueFilterResult.yk;
                  
                // Updating for filtering
                  realValueFiltered_1 = realValueFiltered;
                  realValue_1 = realValue;

                correctedValueFiltered = correctionAlgo(realValueFiltered);

                // Serial monitor outputs  //
                timeAfterAlgo = millis();

                Serial.print(timeAfterAlgo);                  Serial.print(",\t");
                Serial.print(realValue, 4);                   Serial.print(",\t");
                Serial.print(correctedValue, 4);              Serial.print(",\t");
                Serial.print(beforeMeasure);                  Serial.print(",\t");
                Serial.print(afterMeasure);                   Serial.print(",\t");
                Serial.print(realValueFiltered, 4);           Serial.print(",\t");
                Serial.print(correctedValueFiltered, 4);      Serial.print(",\t");
                Serial.print(bSync);                          Serial.print(",\t");
                Serial.print(bSync_corr);                     Serial.print(",\t");
                Serial.print(calibration_factor,4);           Serial.print(",\t");
                //Serial.print(valLue_WU/realvalLue,4);Serial.print(",\t");
                Serial.print((float)scale.get_offset(), 4);   Serial.print(",\t");
                Serial.print(realValue_WU);                   Serial.print(",\t");
                Serial.print(bInactive);                      Serial.print(",\t");
                Serial.print(lastTimeActivity);               Serial.print(",\t");
                Serial.print(myVcc);                          Serial.print(",\t");
                // Serial.print((float)scale.get_Vcc_offset(), 4);Serial.print(",\t");
                
                Serial.print(myAx);                           Serial.print(",\t");
                Serial.print(myAy);                           Serial.print(",\t");
                Serial.print(myAz);                           Serial.print(",\t");
                Serial.print(myGyroX);                        Serial.print(",\t");
                Serial.print(myGyroY);                        Serial.print(",\t");
                Serial.print(myGyroZ);                        Serial.print(",\t");
                
                Serial.print(thetadeg);                       Serial.print(",\t");
                Serial.print(phideg);                         Serial.print(",\t");
                
                Serial.print(myTmp);                          Serial.print(",\t");                
                Serial.print(correctedTempValue);             Serial.print(",\t");
                
                
                
                
                Serial.println("");
                //Serial.print("Activation pin state: "); Serial.println(digitalRead(5));

                // Updating for inactivity check
                displayFinalValue_1 = displayFinalValue;
                displayFinalValue = correctedValueFiltered;
                
              //     Displaying     //
                  if (correctedValueFiltered > MAX_GR_VALUE) { // Verification of the max value in grams
                      do {
                            u8g.setPrintPos(15, 15) ;
                            u8g.print(" OVER");
                            u8g.setPrintPos(15, 40) ;
                            u8g.print("FLOW !");
                        } while(u8g.nextPage());  
                              
                      }
                  else if (correctedValueFiltered < -1*MIN_GR_VALUE){ // Verification of the negative values (with threshold)
                       do {
                            u8g.setFont(u8g_font_osb18);
                            u8g.setPrintPos(17, 30) ; // (Horiz, Vert)
                            u8g.print(" TARE !");

                            u8g.setFont(u8g_font_6x10);
                            u8g.setPrintPos(23, 45) ; // (Horiz, Vert)
                            u8g.print("Negative values");
                            
                        } while(u8g.nextPage());  
                  }
                    else if (abs(thetadeg) > MAX_THETA_VALUE || abs(phideg) > MAX_PHI_VALUE ){ // Verification of the maximum allowed angles
                       do {
                            u8g.setFont(u8g_font_osb18);
                            u8g.setPrintPos(17, 30) ; // (Horiz, Vert)
                            u8g.print(" OUPS !");

                            u8g.setFont(u8g_font_6x10);
                            u8g.setPrintPos(23, 45) ; // (Horiz, Vert)
                            u8g.print("Wooby NOT flat");
                            
                        } while(u8g.nextPage());  
                  }
                  else{
                    // Everything is ok!!  So let's show the measurement
                    do {
                        u8g.setFont(u8g_font_osb18);
                        u8g.setFontPosTop();
                        itoa(displayFinalValue, arrayMeasure, 10);
                        u8g.setPrintPos(DISPLAY_WIDTH/2-u8g.getStrWidth(arrayMeasure)/2, 10) ;
                        u8g.print(int(displayFinalValue), 1);

                        
                        u8g.setFont(u8g_font_osb18);
                        u8g.setFontPosTop();
                        u8g.setPrintPos(30, 25);
                        u8g.print("grams");

                        
                       if (TYPE==0){
                          // Display trust region //
                          u8g.setFont(u8g_font_6x10);
                          u8g.setFontPosBottom();
                          u8g.setPrintPos(5, DISPLAY_HEIGHT-2);
                          // u8g.print(int(displayFinalValue*0.9), 1);
                          u8g.print(int(thetadeg), 10);
                          
  
                          u8g.setFont(u8g_font_6x10);
                          u8g.setFontPosBottom();
                          u8g.setPrintPos(55, DISPLAY_HEIGHT-2);
                          
                          //sprintf(aux, (PGM_P)F("%d %d"), 6, int(TEMPREF));
                          u8g.print(String(int(myTmp)) + "("+ String(int(TEMPREF)) + ")");
                          
                          u8g.setFont(u8g_font_6x10);
                          u8g.setFontPosBottom();
                          u8g.setPrintPos(100, DISPLAY_HEIGHT-2);
                          u8g.print(int(phideg), 10);
                        }

                        // Display batterie levels //
                                                
                          u8g.setFont(u8g_font_6x10);
                          u8g.setFontPosTop();
                          u8g.setPrintPos(100, 12) ; // (Horiz, Vert)
                          u8g.print(int(100*ratioVCCMAX));
                          
                          
                          u8g.setFont(u8g_font_6x10);
                          u8g.setFontPosTop();
                          u8g.setPrintPos(120, 12);
                          u8g.print("%");
                          
                          u8g.drawLine(100,   2,    100+22, 2); // (Horiz, Vert)
                          u8g.drawLine(100,   2+7,  100+22, 2+7);
                          u8g.drawLine(100,   2,    100,    2+7);
                          u8g.drawLine(100+22,2,    100+22, 2+7);
  
                          u8g.drawBox(100+22+1,2+2,2, 7-4+1);                        
                          u8g.drawBox(100+2,2+2,int((22-4+1)*ratioVCCMAX),7-4+1); // (Horiz, Vert, Width, Height)
                        
                    } while(u8g.nextPage());
                  }

              if (TYPE>0){
                inactivityCheck();
                if (bInactive){
                  Serial.println("Display set to inactive");
                }
              }

      break;
      
      default:
      break;
    } 
        
  }
