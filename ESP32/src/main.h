extern bool BF_SERIALPORT;
extern bool BF_BLUETOOTH;
extern float calibrationFactor;
extern float relativeVal_WU;
extern float realValue_WU_AngleAdj;
extern float realValue_WU_MovAvg;
extern float realValue_WU_Filt;
extern float TEMPREF;
extern HX711 scale;
extern String genericJSONString;

extern void myTare();
extern void handleActionInactivity();   // (PH) TBR when creating source code for inactivity
extern void inactivityCheck();          // (PH) TBR when creating source code for inactivity