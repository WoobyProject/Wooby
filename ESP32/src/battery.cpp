#include <Arduino.h>
#include <math.h>
#include "mapping.h"
#include "battery.h"

float vccReadBits = 0;      // Voltage read by the ADC (in bits)
float vccReadVolts = 0;     // Voltage read by the ADC (in Volts)
float vccGPIO = 0;          // Real voltage on the GPIO pin (in Volts)
float vccVolts = 0;         // Real voltage of Vcc (in Volts)
float ratioVCCMAX = 0;      // Percentage of the read voltage in Vcc to the full charge voltage

const int N_VCC_READ = 10;
const float VCCMIN   = 5.0;         // Minimum expected Vcc level, in Volts.
const float VCCMAX   = 7.3;         // Maximum expected Vcc level, in Volts.
const float realMeasureVcc =      7.270;
const float realMeasureDivider =  2.355;
const float realMeasureADC =      2.154;
const float RATIO_VCC_DIV = realMeasureVcc/realMeasureDivider;
const float RATIO_VCC_ADC = realMeasureVcc/realMeasureADC;
const float RATIO_DIV_ADC = realMeasureDivider/realMeasureADC;

float K_BITS_TO_VOLTS = 3.3/4095;

float readPinAnalogAvg(int n)
{
  int sum = 0;
  for (int i=0; i< n; i++)
  {
    sum += analogRead(PIN_VCC);
    // Serial.println(readVal);
  }
  return float(sum)/n;
}

float mapval(float x, float  in_min, float  in_max, float  out_min, float out_max)
{
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void readVcc()
{
  // Reading pin
  //Old: float(analogRead(PIN_VCC));
  vccReadBits = readPinAnalogAvg(N_VCC_READ);
  vccReadVolts = vccReadBits*K_BITS_TO_VOLTS;

  // Calulation for displaying
  vccGPIO   = vccReadVolts*RATIO_DIV_ADC;
  vccVolts  = vccReadVolts*RATIO_VCC_ADC;
  // ratioVCCMAX = min((vccVolts/VCCMAX), float(1.0));
  ratioVCCMAX = mapval(vccVolts, VCCMIN, VCCMAX, 0, 1);
  ratioVCCMAX = fmaxf(fminf(ratioVCCMAX, float(1.0)), float(0.0));

  /*
  Serial.printf("\nVoltage read (bits): %f", vccBits);
  Serial.printf("\nReal GPIO voltage (V): %f",   vccGPIO);
  Serial.printf("\nVCC_RATIO(V): %f",   VCC_RATIO);
  Serial.printf("\nImage to Vcc (V): %f ",   vccVolts);
  Serial.printf("\nRatio to Vcc (%%): %f \n", int(100*ratioVCCMAX));
*/
}

void setupVccMgnt()
{
  analogReadResolution(12);
  analogSetWidth(12);
  analogSetPinAttenuation(PIN_VCC,ADC_11db); // ADC_11db provides an attenuation so that IN/OUT = 1 / 3.6 an input of 3 volts is reduced to 0.833 volts before ADC measurement

  readVcc();
}
