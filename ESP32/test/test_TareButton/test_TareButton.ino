const byte interruptPin = 27;

volatile int interruptCounterRising = 0;
volatile int interruptCounterFalling = 0;
int numberOfInterrupts = 0;

long unsigned timeBefore = 0;
long unsigned timeAfter  = 0;
bool bEnd = false;

portMUX_TYPE muxRising  = portMUX_INITIALIZER_UNLOCKED;
portMUX_TYPE muxFalling = portMUX_INITIALIZER_UNLOCKED;
  
void IRAM_ATTR handleInterruptRising() {
  //portENTER_CRITICAL_ISR(&muxRising);
  interruptCounterRising++;
  timeBefore = millis();
  Serial.println("Rising ");
  //portEXIT_CRITICAL_ISR(&muxRising);
}

void IRAM_ATTR handleInterruptFalling() {
  //portENTER_CRITICAL_ISR(&muxFalling);
  interruptCounterFalling++;
  timeAfter = millis();
  Serial.println("Falling ");
  bEnd = true;
  //portEXIT_CRITICAL_ISR(&muxFalling);
}

void setup() {
 
  Serial.begin(115200);
  Serial.println("Monitoring interrupts: ");
  pinMode(interruptPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterruptRising,  RISING );  // FALLING
  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterruptFalling, FALLING ); // FALLING
 
}
 
void loop() {
  /*
  if(interruptCounterFalling>0){
 
      portENTER_CRITICAL(&muxFalling);
      interruptCounterFalling--;
      portEXIT_CRITICAL(&muxFalling);
 
      numberOfInterrupts++;
      Serial.print("An interrupt has occurred. Total: ");
      Serial.println(numberOfInterrupts);
  }
  */
  
  if (bEnd){
    Serial.print("Time: ");
    Serial.println((timeAfter-timeBefore)/1000);
    bEnd = false;
  }
  
}
