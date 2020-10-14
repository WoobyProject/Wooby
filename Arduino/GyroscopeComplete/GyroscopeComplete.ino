// (c) Michael Schoeffler 2017, http://www.mschoeffler.de
#include "Wire.h" // This library allows you to communicate with I2C devices.
#include <math.h>

const int MPU_ADDR = 0x68; // I2C address of the MPU-6050. If AD0 pin is set to HIGH, the I2C address will be 0x69.
int16_t accelerometer_x, accelerometer_y, accelerometer_z; // variables for accelerometer raw data
int16_t gyro_x, gyro_y, gyro_z; // variables for gyro raw data
int16_t temperature; // variables for temperature data
char tmp_str[7]; // temporary variable used in convert function

const float pi = 3.1416;

char* convert_int16_to_str(int16_t i) { // converts int16 to string. Moreover, resulting strings will have the same length in the debug monitor.
  sprintf(tmp_str, "%6d", i);
  return tmp_str;
}

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

void setup() {
  
  Serial.begin(115200);

  setupMPU();

}


void loop() {

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); // starting with register 0x3B (ACCEL_XOUT_H) [MPU-6000 and MPU-6050 Register Map and Descriptions Revision 4.2, p.40]
  Wire.endTransmission(false); // the parameter indicates that the Arduino will send a restart. As a result, the connection is kept active.
  Wire.requestFrom(MPU_ADDR, 7 * 2, true); // request a total of 7*2=14 registers

  // "Wire.read()<<8 | Wire.read();" means two registers are read and stored in the same variable
  accelerometer_x = Wire.read() << 8 | Wire.read(); // reading registers: 0x3B (ACCEL_XOUT_H) and 0x3C (ACCEL_XOUT_L)
  accelerometer_y = Wire.read() << 8 | Wire.read(); // reading registers: 0x3D (ACCEL_YOUT_H) and 0x3E (ACCEL_YOUT_L)
  accelerometer_z = Wire.read() << 8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)
  temperature =     Wire.read() << 8 | Wire.read(); // reading registers: 0x41 (TEMP_OUT_H) and 0x42 (TEMP_OUT_L)
  gyro_x =          Wire.read() << 8 | Wire.read(); // reading registers: 0x43 (GYRO_XOUT_H) and 0x44 (GYRO_XOUT_L)
  gyro_y =          Wire.read() << 8 | Wire.read(); // reading registers: 0x45 (GYRO_YOUT_H) and 0x46 (GYRO_YOUT_L)
  gyro_z =          Wire.read() << 8 | Wire.read(); // reading registers: 0x47 (GYRO_ZOUT_H) and 0x48 (GYRO_ZOUT_L)

  // print out data

  /*
    Serial.print(millis());               Serial.print(",\t");

    // Serial.print(   "aX = ");
    Serial.print(float(accelerometer_x)); Serial.print(",\t");

    // Serial.print(" | aY = ");
    Serial.print(float(accelerometer_y)); Serial.print(",\t");

    // Serial.print(" | aZ = ");
    Serial.print(float(accelerometer_z)); Serial.print(",\t");


    // the following equation was taken from the documentation [MPU-6000/MPU-6050 Register Map and Description, p.30]
    // Serial.print(" | tmp = ");
    Serial.print(temperature/340.00+36.53);Serial.print(",\t");

    // Serial.print(" | gX = ");
    Serial.print(float(gyro_x));            Serial.print(",\t");

    //Serial.print(" | gY = ");
    Serial.print(float(gyro_y));            Serial.print(",\t");

    //Serial.print(" | gZ = ");
    Serial.print(float(gyro_z));            Serial.print(",\t");

    Serial.println();

float myAx = float(accelerometer_x)/16384;
  float myAy = float(accelerometer_y)/16384;
  float myAz = float(accelerometer_z)/16384;

float myAx = -1*float(accelerometer_x)/16384;
  float myAy =    float(accelerometer_z)/16384;
  float myAz = -1*float(accelerometer_y)/16384;

  
  */
  float myAx = float(accelerometer_x)/16384;
  float myAy = -1*float(accelerometer_z)/16384;
  float myAz = float(accelerometer_y)/16384;
  
  float myGyroX = float(gyro_x)/131;
  float myGyroY = float(gyro_y)/131;
  float myGyroZ = float(gyro_z)/131;
  
  
  // Serial.print(   "aX = ");
  Serial.print(myAx); Serial.print(",\t");

  // Serial.print(" | aY = ");
  Serial.print(myAy); Serial.print(",\t");

  // Serial.print(" | aZ = ");
  Serial.print(myAz); Serial.print(",\t");

  // Serial.print(   "gyroX = ");
  Serial.print(myGyroX); Serial.print(",\t");

  // Serial.print(" | gyroY = ");
  Serial.print(myGyroY); Serial.print(",\t");

  // Serial.print(" | gyroZ = ");
  Serial.print(myGyroZ); Serial.print(",\t");  

  float phi = (180/pi)*atan2(-1*myAx, sqrt(pow(myAz,2) + pow(myAy,2)));
  float theta =  (180/pi)*atan2(myAy,myAz);
  
  Serial.print(int(theta));Serial.print(",\t");
  Serial.print(int(phi));Serial.print(",\t"); 
  
  Serial.println();

  // delay
  delay(100);
}
