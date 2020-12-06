/*
  Name:		Sequence.ino
  Created:	9/5/2018 10:49:52 AM
  Author:	Evert Arias
  Description: Example to demostrate how to use the library to detect a sequence of presses on a button.
*/

#include <EasyButton.h>

// Arduino pin where the button is connected to.
#define BUTTON_PIN 27

#define BAUDRATE 115200

// Instance of the button.
// EasyButton button(BUTTON_PIN);
EasyButton button(BUTTON_PIN, 50, true, true); 

// Callback function to be called when the button is pressed.
void onSequenceMatched()
{
  Serial.println("Button pressed");
}

void onSequenceMatched1()
{
  Serial.println("Button pressed only once! ");
}

void onPressedForDuration() {
    Serial.println("Button has been pressed for the given duration!");
}

void onPressedForDuration2() {
    Serial.println("Button has been pressed for the 2 seconds!");
}


void buttonISR()
{
  // When button is being used through external interrupts, parameter INTERRUPT must be passed to read() function.
  Serial.println("on ISR! ");

  
  button.read();
  
  if (button.pressedFor(2000)){
    Serial.println("Pressed for 2000");
  }
  
  

  Serial.println("out of ISR");
}

void setup()
{
  // Initialize Serial for debuging purposes.
  Serial.begin(BAUDRATE);

  Serial.println();
  Serial.println(">>> EasyButton sequence example <<<");

  // Initialize the button.
  button.begin();
  // Add the callback function to be called when the given sequence of presses is matched.
  // button.onSequence(5 /* number of presses */, 5000 /* timeout */, onSequenceMatched /* callback */);
  // button.onPressedFor(5000, onPressedForDuration);
  // button.onPressedFor(2000, onPressedForDuration2);
  
  button.onSequence(1 /* number of presses */, 100 /* timeout */, onSequenceMatched1 /* callback */);

  if (button.supportsInterrupt())
  {
    button.enableInterrupt(buttonISR);
    Serial.println("Button will be used through interrupts");
  }
  else{
    Serial.print("NO SUPPORT FOR INTERRUPT! ");
  }
  
}

void loop()
{
  // Continuously read the status of the button.
  button.update();
  Serial.println("Waiting start");
  delay(1000);
  Serial.println("Waiting end");

  if (button.pressedFor(2000)){
    Serial.println("Print for 2000");
  }
  
}
