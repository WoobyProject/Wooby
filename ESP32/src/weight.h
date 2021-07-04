extern const int N_WINDOW_MOV_AVG;
extern RunningAverage weightMovAvg;
extern bool bSync;
extern unsigned long tBeforeMeasure;
extern unsigned long tAfterMeasure;
extern unsigned long tAfterAlgo;
extern float realValueFiltered;
extern float realValue_WU;
extern RTC_DATA_ATTR float offset;
extern float realValue;
extern float correctedValueFiltered;
extern NormalizingIIRFilter<2, 2, float> filterWeight;

extern void setUpWeightAlgorithm();
extern void getWoobyWeight();