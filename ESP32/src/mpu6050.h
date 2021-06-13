#define MAX_THETA_VALUE (float)10.0
#define MAX_PHI_VALUE (float)10.0

extern int16_t Ax,Ay,Az,Tmp,Gx,Gy,Gz;
extern float myAx, myAy, myAz, myTmp, myGx, myGy, myGz;
extern float thetadeg, phideg;
extern bool BF_MPU;

extern void setupMPU();
extern void readMPU();
extern void angleAdjustment();