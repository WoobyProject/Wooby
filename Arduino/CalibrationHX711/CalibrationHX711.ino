/*
 Started with example code written by Nathan Seidle from SparkFun Electronics and added
 LCD output with gram and ounce values.
 
 Setup your scale and start the sketch WITHOUT a weight on the scale
 Once readings are displayed place the weight on the scale
 Press +/- or a/z to adjust the calibration_factor until the output readings match the known weight
 Arduino pin 6 -> HX711 CLK
 Arduino pin 5 -> HX711 DOUT
 Arduino pin 5V -> HX711 VCC
 Arduino pin GND -> HX711 GND
 
 The HX711 board can be powered from 2.7V to 5V so the Arduino 5V power should be fine.
 
 The HX711 library can be downloaded from here: https://github.com/bogde/HX711
*/



#include "HX711.h"

#define DOUT 6
#define CLK  5

HX711 scale(DOUT, CLK);
int nMeasures = 10;

float calibration_factor = 42.3;//2125; //-7050 worked for my 440lb max scale setup
float units;
float ounces;

void setup() {
  Serial.begin(9600);


  Serial.println("HX711 calibration sketch");
  Serial.println("Remove all weight from scale");
  Serial.println("After readings begin, place known weight on scale");
  Serial.println("Press + or a to increase calibration factor");
  Serial.println("Press - or z to decrease calibration factor");


  scale.set_gain(64); //lolo: test avec un codage des valeurs lues en 64bits au lieu de 128 bits.
  scale.set_scale(calibration_factor);  // lolo: mesure obtenue avec le sketch CalibrageHX711Spartfunk56.ino
      
  scale.tare();  //Reset the scale to 0

  long zero_factor = scale.read_average(); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);
}

void loop() {

  scale.set_scale(calibration_factor); //Adjust to this calibration factor

  Serial.print("Reading: ");
  units = scale.get_units(nMeasures);
  /*if (units < 0) {
    units = 0.00;
  }*/
  
  ounces = units * 0.035274;
  Serial.print(units);
  Serial.print(" grams"); 
  Serial.print(" calibration_factor: ");
  Serial.print(calibration_factor);
  Serial.println();

  /*Serial.print("Grams: ");
  Serial.print(units);

  Serial.print(" . Ounce: ");
  Serial.println(ounces);
  

  Serial.print("Calbr: ");
  Serial.println(calibration_factor);
*/

  if(Serial.available())
  {
    char temp = Serial.read();
    if(temp == '+' || temp == 'a')
      calibration_factor += 0.1;
    else if(temp == '-' || temp == 'z')
      calibration_factor -= 0.1;
    else if(temp == 't')
      scale.tare(); 
  }
}
