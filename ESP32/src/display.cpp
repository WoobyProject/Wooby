#include <U8g2lib.h>                 // by Oliver
#include <ArduinoJson.h>
#include "version.h"
#include "display.h"
#include "battery.h"
#include "bluetooth_com.h"
#include "inactivity.h"
#include "mpu6050.h"
#include "serial_com.h"
#include "tare.h"
#include "WoobyImage.h"
#include "WoobyWiFi.h"

#define FLIP_MODE 0
#define DISPLAY_WIDTH 128
#define DISPLAY_HEIGHT 64
#define NSTATES_SETUP 12

bool BF_DISPLAY = false;
int setupState = 0;
float MAX_GR_VALUE = 11000; // in gr
float MIN_GR_VALUE = 5;    // in gr
// For Arduino:
//  U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_DEV_0|U8G_I2C_OPT_NO_ACK|U8G_I2C_OPT_FAST); // Fast I2C / TWI
// For ESP32:
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

void setupDisplay()
{
  try
  {
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
  catch(int e)
  {
    Serial.println("Not possible to activate the display");
    BF_DISPLAY = true;
  }
}

void initDisplay(const unsigned char * u8g_image_bits)
{
  u8g.firstPage();
  do
  {
    u8g.drawXBMP( 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, u8g_image_bits);
    // Serial.printf("Setup display value:%d\n\n",   int(float(DISPLAY_WIDTH)*float(setupState)/float(NSTATES_SETUP))  );
    u8g.drawBox(0,DISPLAY_HEIGHT-5,  int(float(DISPLAY_WIDTH)*float(setupState)/float(NSTATES_SETUP))   , 5); // (Horiz, Vert, Width, Height)
  } 
  while( u8g.nextPage() );
}

void displayImage(const unsigned char * u8g_image_bits)
{
   u8g.firstPage();
   do
   {
       u8g.drawXBMP( 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, u8g_image_bits);
   } 
   while( u8g.nextPage() );

   delay(4000);
}

void poweredByDisplay(void)
{
  Serial.println("");
  Serial.println("Displaying Powered by ...");

 // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do 
  {
      u8g.setFont(u8g2_font_6x10_tf);
      u8g.drawStr( 30, 15, "Powered by");
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 10, 40, "Humanity");
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 40, 60, "Lab");
  }
  while(u8g.nextPage());

  Serial.println("Waiting 1 sec...");
  delay(1000);
  Serial.println("");
}

void sponsorsDisplay(void)
{
  Serial.println("");
  Serial.println("Displaying Sponsors..");

  // Set up the display
    u8g.firstPage();
    u8g.setFont(u8g2_font_osb18_tf);

  // Display loop
   do 
   {
      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 15, 25, "AIRBUS");

      u8g.setFont(u8g2_font_6x10_tf);
      u8g.drawStr( 60, 35, "&");

      u8g.setFont(u8g2_font_osb18_tf);
      u8g.drawStr( 15, 55, "MEDAIR");
   }
   while(u8g.nextPage());

  Serial.println("Waiting 1 sec...");
  delay(1000);
  Serial.println("");
}

void wakingUpDisplay()
{
  // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do
  {
    u8g.setFont(u8g2_font_6x10_tf); //u8g2_font_6x10_tf
    u8g.drawStr( 45, 10, "Woooooby!");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 20, 20, "Waking up");
  }
  while(u8g.nextPage());
  delay(1000);
}

void sleepingDisplay()
{

  // Set up the display
  u8g.firstPage();
  u8g.setFont(u8g2_font_osb18_tf);

  do
  {
    u8g.setFont(u8g2_font_6x10_tf); //u8g2_font_6x10_tf
    u8g.drawStr( 50, 10, "zzz");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 20, 25, "Going to");
    u8g.setFont(u8g2_font_osb18_tf);
    u8g.drawStr( 40, 40, "sleep");
  }
  while(u8g.nextPage());

  delay(2000);
}

void nextStepSetup()
{
  setupState++;
  initDisplay(logoWooby);
}

void mainDisplayWooby(float measure)
{
  char arrayMeasure[8];

  // Set up the display
  u8g.firstPage();

  if (measure > MAX_GR_VALUE)  // Verification of the max value in grams
  {
      do
      {
            u8g.setCursor(15, 15) ;
            u8g.print(" OVER");
            u8g.setCursor(15, 40) ;
            u8g.print("FLOW !");
        }
        while(u8g.nextPage());
  }
  else if ((measure < -1*MIN_GR_VALUE)  && (B_INHIB_NEG_VALS))  // Verification of the negative values (with threshold)
  {
       do 
       {
            u8g.setFont(u8g2_font_osb18_tf);
            u8g.setCursor(17, 25) ; // (Horiz, Vert)
            u8g.print(" TARE !");

            u8g.setFont(u8g2_font_6x10_tf);
            u8g.setCursor(23, 45) ; // (Horiz, Vert)
            u8g.print("Negative values");

        }
        while(u8g.nextPage());
  }
  else if ((abs(thetadeg) > MAX_THETA_VALUE || abs(phideg) > MAX_PHI_VALUE ) && (B_LIMITED_ANGLES))  // Verification of the maximum allowed angles
  {
       do
       {
            u8g.setFont(u8g2_font_osb18_tf);
            u8g.setCursor(17, 20) ; // (Horiz, Vert)
            u8g.print(" OUPS !");

            u8g.setFont(u8g2_font_6x10_tf);
            u8g.setCursor(23, 45) ; // (Horiz, Vert)
            u8g.print("Wooby NOT flat");

        }
        while(u8g.nextPage());
  }
  else  // Everything is ok!!  So let's show the measurement
  {
    do
    {
        // Display weight //
        u8g.setFont(u8g2_font_osb18_tf);
        u8g.setFontPosTop();
        itoa(measure, arrayMeasure, 10);
        u8g.setCursor(DISPLAY_WIDTH/2-u8g.getStrWidth(arrayMeasure)/2, 15) ;
        u8g.print((measure), 0);


        u8g.setFont(u8g2_font_osb18_tf);
        u8g.setFontPosTop();
        u8g.setCursor(30, 30);
        u8g.print("grams");

        if (B_DEBUG_MODE)
        {
          // Display MPU values //
          if (B_DISPLAY_ANGLES)
          {
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

          if (B_DISPLAY_ACCEL)
          {
            u8g.setFont(u8g2_font_6x10_tf);

            u8g.setCursor(4, 24);
            BF_MPU? u8g.print("???"):u8g.print(roundf(myAx*100.0)/100.0);

            u8g.setCursor(4, 31);
            BF_MPU? u8g.print("???"):u8g.print(roundf(myAy*100.0)/100.0);

            u8g.setCursor(4, 38);
            BF_MPU? u8g.print("???"):u8g.print(roundf(myAz*100.0)/100.0);
          }

          u8g.setFont(u8g2_font_micro_tr);
          if (B_DEBUG_MODE)
          {
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

          if (false)
          { //BF_SERIALPORT
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
          else
          {
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

    }
    while(u8g.nextPage());
  }

  if (B_INACTIVITY_ENABLE)
  {
    inactivityCheck();
    handleActionInactivity();
  }
}