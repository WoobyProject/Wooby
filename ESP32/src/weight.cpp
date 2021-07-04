#include <math.h>
#include <RunningAverage.h>
#include "Filters/IIRFilter.hpp"
#include "HX711.h"
#include <U8g2lib.h>                 // by Oliver
#include "weight.h"
#include "display.h"
#include "main.h"
#include "mpu6050.h"

const int nMeasures = 7;
const int N_WINDOW_MOV_AVG = nMeasures;
RunningAverage weightMovAvg(N_WINDOW_MOV_AVG);
bool bSync;
unsigned long bSyncTimer = 0;
unsigned long tBeforeMeasure = 0;
unsigned long tAfterMeasure = 0;
unsigned long tAfterAlgo = 0;
float realValueFiltered;
float realValue_WU = 0;
RTC_DATA_ATTR float offset;
float realValue;
float correctedValueFiltered = 0;
// Definition of the coeffs for the filter
// Remember : Te = nMeasures*100 ms
//            b = 1 - math.exp(-Te/tau)
//            a = math.exp(-Te/tau)
//            tau = 1.4
const float b =  0.3915; // Te = nMeasures*100 ms
const float a =  0.6085; //
// Filter = y/u = b*z-1(1-a)
NormalizingIIRFilter<2, 2, float> filterWeight = {{0, b}, {1, -a}};


const float FILTERING_THR = 20;  // in grams
const unsigned long BSYNC_TIME = 2000;

float realValue_1;
float realValueFiltered_1;
float relativeVal_WU = 0;
float relativeVal_WU_1;
float realValue_WU_AngleAdj = 0;
float realValue_WU_MovAvg = 0;
float realValue_WU_Filt = 0;

float correctionAlgo(float realValue){

  int realValueInt = int(realValue);
  float realValueDecim = (realValue - float(realValueInt)) ;
  float correctedValue = 0;

  // Around zero values deletion //
    if (realValue<=MIN_GR_VALUE && realValue>=-1*MIN_GR_VALUE){
      return correctedValue = 0.0;
    }

  // Round algorithm //
    if ( realValueDecim < 0.4) { correctedValue = long(realValueInt);}
    if ( realValueDecim >= 0.4 && realValueDecim <= 0.7) { correctedValue = long(realValueInt)+0.5 ; }
    if ( realValueDecim > 0.7) { correctedValue = long(realValueInt)+1; }

  return correctedValue;
}

void setUpWeightAlgorithm()
{
    realValue_1 = 0;
    realValueFiltered = 0;
    realValueFiltered_1 = 0;
    bSync = false;

    weightMovAvg.clear();
    weightMovAvg.fillValue(0, N_WINDOW_MOV_AVG); // (float)scale.get_offset()
}

void getWoobyWeight()
{

    // Updating for synchro
    relativeVal_WU_1 = relativeVal_WU;

    // Raw weighting //
    tBeforeMeasure = millis();
    realValue_WU = scale.read_average(nMeasures);
    tAfterMeasure = millis();

    offset = (float)scale.get_offset();
    relativeVal_WU = realValue_WU - offset;

    // Synchronization calcualtion

    if (abs(relativeVal_WU-relativeVal_WU_1) > FILTERING_THR*scale.get_scale())
    {
      bSyncTimer = millis();
      bSync = true;
    }
    else
    {
      if (millis()-bSyncTimer > BSYNC_TIME)
      {
        bSync = false;}
      else
      {
        bSync = true;
      }
    }

    // Angles correction //
    angleAdjustment();

    // Moving average //
    if (bSync)
    {
      weightMovAvg.fillValue(realValue_WU_AngleAdj, N_WINDOW_MOV_AVG);
      realValue_WU_MovAvg = realValue_WU_AngleAdj;
    }
    else
    {
      weightMovAvg.addValue(realValue_WU_AngleAdj);
      realValue_WU_MovAvg = weightMovAvg.getFastAverage(); // or getAverage()
    }

    // Filtering with Arduino-Filters library
    if (bSync)
    {
      realValue_WU_Filt = realValue_WU_MovAvg;
      filterWeight.reset(realValue_WU_MovAvg);
    }
    else
    {
      realValue_WU_Filt = filterWeight(realValue_WU_MovAvg);
    }


    // Conversion to grams //
    realValue = realValue_WU_Filt/scale.get_scale(); // (realValue_WU_AngleAdj)/scale.get_scale();
    /*
    correctedValue = correctionAlgo(realValue); // NOT USED!!!!!

    // Filtering  //

      // Filtering for the real value //
      realValueFilterResult = filtering(realValue, realValue_1, realValueFiltered_1);
      bSync = realValueFilterResult.bSync;
      realValueFiltered = realValueFilterResult.yk;

      // Updating for filtering
      realValueFiltered_1 = realValueFiltered;
      realValue_1 = realValue;
    */

    // Final correction  //
    correctedValueFiltered = correctionAlgo(realValue);

    tAfterAlgo = millis();
}