extern bool BF_SERIALPORT;
extern bool BF_BLUETOOTH;
extern bool bSync;
extern unsigned long tBeforeMeasure;
extern unsigned long tAfterMeasure;
extern unsigned long tAfterAlgo;
extern RTC_DATA_ATTR float offset;
extern float calibrationFactor;
extern float realValue_WU;
extern float relativeVal_WU;
extern float realValue_WU_AngleAdj;
extern float realValue_WU_MovAvg;
extern float realValue_WU_Filt;
extern float realValue;
extern float correctedValueFiltered;
extern float realValueFiltered;
extern float TEMPREF;

extern void handleActionInactivity();   // (PH) TBR when creating source code for inactivity
extern void inactivityCheck();          // (PH) TBR when creating source code for inactivity