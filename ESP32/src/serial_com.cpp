#include <ArduinoJson.h>            // by Benoit Blanchon
#include "version.h"
#include "serial_com.h"
#include "battery.h"
#include "main.h"
#include "mpu6050.h"

bool BF_SERIALPORT = false;

// See https://arduinojson.org/v6/assistant/
const int N_FIELDS_JSON = 36;
const size_t CAPACITY_JSON = JSON_OBJECT_SIZE(N_FIELDS_JSON) + 0; //1620
DynamicJsonDocument genericJSON(CAPACITY_JSON);

bool buildGenericJSON()
{
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