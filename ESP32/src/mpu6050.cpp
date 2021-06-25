#include <Wire.h>
#include <math.h>
#include "version.h"
#include "mpu6050.h"
#include "main.h"

  // Model choice
  #if MODEL <= 4
    float K_MYAX_X = -1; float K_MYAX_Y = 0; float K_MYAX_Z = 0;
    float K_MYAY_X =  0; float K_MYAY_Y = 1; float K_MYAY_Z = 0;
    float K_MYAZ_X =  0; float K_MYAZ_Y = 0; float K_MYAZ_Z = 1;
  #endif

  #if MODEL == 5
    float K_MYAX_X =  0; float K_MYAX_Y = 0; float K_MYAX_Z = 1;
    float K_MYAY_X = -1; float K_MYAY_Y = 0; float K_MYAY_Z = 0;
    float K_MYAZ_X =  0; float K_MYAZ_Y = 1; float K_MYAZ_Z = 0;
  #endif

#define MPU_ADDR 0x68
const float pi = 3.1416;
const float calib_theta_2 = -0.00014;

int16_t Ax,Ay,Az,Tmp,Gx,Gy,Gz;
float myAx, myAy, myAz, myTmp, myGx, myGy, myGz;
float thetadeg, phideg;
bool BF_MPU = false;

void setupMPU()
{
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

void readMPU(){

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  uint8_t errorRF = Wire.requestFrom(MPU_ADDR,14,true);

  if(errorRF)
  {
    BF_MPU = false;

    Ax =  Wire.read()<<8 | Wire.read(); // reading registers: 0x3B and 0x3C
    Ay =  Wire.read()<<8 | Wire.read(); // reading registers: 0x3D and 0x3E
    Az =  Wire.read()<<8 | Wire.read(); // reading registers: 0x3F and 0x40
    Tmp = Wire.read()<<8 | Wire.read(); // reading registers: 0x41 and 0x42
    Gx =  Wire.read()<<8 | Wire.read(); // reading registers: 0x43 and 0x44
    Gy =  Wire.read()<<8 | Wire.read(); // reading registers: 0x45 and 0x46
    Gz =  Wire.read()<<8 | Wire.read(); // reading registers: 0x47 and 0x48

    myAx = (K_MYAX_X*float(Ax)+K_MYAX_Y*float(Ay)+K_MYAX_Z*float(Az))/16384;
    myAy = (K_MYAY_X*float(Ax)+K_MYAY_Y*float(Ay)+K_MYAY_Z*float(Az))/16384;
    myAz = (K_MYAZ_X*float(Ax)+K_MYAZ_Y*float(Ay)+K_MYAZ_Z*float(Az))/16384;

    myGx =    float(Gx)/131;
    myGy =    float(Gy)/131;
    myGz =    float(Gz)/131;

    myTmp = Tmp/340.00+36.53;
  }
  else
  {
    // Serial.println("ERROR: Reading MPU");
    BF_MPU = true;
  }
}

void angleCalc()
{
  readMPU(); // This function also updates BF_MPU
  // Keep in mind that atan2() handles the zero div
  phideg = (180/pi)*atan2(myAy,myAz);
  thetadeg =   (180/pi)*atan2(-1*myAx, sqrt(pow(myAz,2) + pow(myAy,2)));
}

void angleAdjustment()
{
  angleCalc(); // angleCalc() also updates BF_MPU
  if(!BF_MPU && B_ANGLE_ADJUSTMENT)
  {
    realValue_WU_AngleAdj = relativeVal_WU/(1+calib_theta_2*pow( fminf(fabsf(thetadeg), MAX_THETA_VALUE) , 2));
  }
  else
  {
    realValue_WU_AngleAdj = relativeVal_WU;
  }
}