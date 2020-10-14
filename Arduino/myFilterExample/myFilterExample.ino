#include "Filter.h"

float Ts = 0.1;
float tau = 2;
Filter myFilter(Ts,  tau);

void setup() {
  // put your setup code here, to run once:
   Serial.begin(115200);
   myFilter.init();
   
  randomSeed(analogRead(0));

}

void loop() {
  // put your main code here, to run repeatedly:

  float error = 0*random(-10, 10);
  float stepMag = 100;

  float inputSignal;
  
  if ((millis()/int(7*tau*1000))%2)
    inputSignal = stepMag + error;
  else
    inputSignal = 0;
  
  float filteredSignal = myFilter.update(inputSignal);

  Serial.print(float(millis()));
  Serial.print(",\t");
  Serial.print(inputSignal);
  Serial.print(",\t");
  Serial.print(filteredSignal); 
  Serial.print(",\t");
  Serial.print(0);
  Serial.println(", ");
  delay(50);
  
}
