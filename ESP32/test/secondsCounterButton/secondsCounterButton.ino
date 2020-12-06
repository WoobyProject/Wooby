/*
  Name:    TouchButton.ino
  Created: 6/25/2019 9:25:52 AM
  Author:  Evert Arias
  Description: Example to demostrate how to use the library to detect a single touch.
*/

#include <EasyButtonTouch.h>

unsigned long count = 0;
unsigned long tPressed = 0;

// Arduino pin where the button is connected to.
#define BUTTON_PIN 27

#define BAUDRATE 115200

// Instance of the button.
// EasyButtonTouch button(BUTTON_PIN);
EasyButton button(BUTTON_PIN, 50, true, true); 


// Callback function to be called when the button is pressed.
void onPressed()
{
  //Serial.println("Button has been pressed");
  
}

void setup()
{
  // Initialize Serial for debuging purposes.
  Serial.begin(BAUDRATE);

  Serial.println();
  Serial.println(">>> EasyButton touch button example <<<");

  // Initialize the button.
  button.begin();
  // Add the callback function to be called when the button is pressed.
  button.onPressed(onPressed);
}

void loop()
{
  // Continuously read the status of the button.
  button.read();

  if (button.wasPressed()){
    Serial.println("Button pressed! ");
    count = millis();
  }
  if (button.wasReleased()){
    Serial.println("Button released! ");
    tPressed =  millis()-count;
    Serial.printf("for %d ", tPressed);  }
      
  if(tPressed>10000)
    Serial.println("Debug mode");
}
