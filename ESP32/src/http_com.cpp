#include "version.h"
#include "Debugging.h"
#include "http_com.h"
// For encryption
/*
#include <SHA256.h>
#include <rBase64.h>                //  by boseji
*/

#ifdef B_GOOGLE_HTTPREQ

  bool setupGoogleComs()
  {
    if (!B_GOOGLE_HTTPREQ){
      Serial.printf("\nWARNING: Google comms are disabled.");
      return false;
    }

    // Verifying WiFi connection
    BF_WIFI = !checkWiFiConnection();
    if (BF_WIFI){
      Serial.printf("\nWARNING: WiFi is disabled. Google comms wiil be disabled too.");
      return false;
    }

    // Connexion to Google
    clientForGoogle.setCACert(root_ca);

  }

  void hashJSON(char* data, unsigned len)
  {
    // Hash encryption of the JSON
    sha.resetHMAC(key, sizeof(key));
    sha.update(data, len);
    sha.finalizeHMAC(key, sizeof(key), hmacResult, sizeof(hmacResult));
    DPRINTLN("DataSize :" + String(len));
    DPRINTLN(data);
    DPRINTLN("HashSize :" + String(sha.hashSize( )));
    DPRINTLN("BlockSize:" + String(sha.blockSize()));
    sha.clear();
  }

  String buildJson()
  {
    Serial.println("IP ADDRESS");
    Serial.println(getIp());

    dataItem["tBeforeMeasure"     ]     = tBeforeMeasure;
    dataItem["tAfterMeasure"     ]      = tAfterMeasure;
    dataItem["IPadress" ]               = getIp();
    dataItem["realValueFiltered"     ]  = realValueFiltered;
    dataItem["correctedValueFiltered"]  = correctedValueFiltered;
    dataItem["bSync"     ]              = bSync;
    dataItem["calibrationFactor"     ] = calibrationFactor;
    dataItem["offset"]                  = offset;
    dataItem["realValue_WU"     ]       = realValue_WU;
    dataItem["bInactive"]               = bInactive;
    dataItem["lastTimeActivity"     ]   = lastTimeActivity;
    dataItem["myAx"]                    = myAx;
    dataItem["myAy"]                    = myAy;
    dataItem["myAz"]                    = myAz;
    dataItem["thetadeg"]                = thetadeg;
    dataItem["phideg"]                  = phideg;
    dataItem["myTmp"]                   = myTmp;
    dataItem["TEMPREF"]                 = TEMPREF;
    dataItem["MODEL"]                   = MODEL;

    char name[] = "Wooby";
    // strcat(ARDUINO_BOARD,name);
    dataItem["ThisBoard"] =  name; //<char*>

    // Put the json in a string
    String jsonStr;
    serializeJson(dataItem, jsonStr);
    // Put the json string in char array
    char chBuf[jsonStr.length()];
    jsonStr.toCharArray(chBuf, jsonStr.length()+1);

    DPRINTLN("jsonStr :" + String(jsonStr));
    DPRINTLN("chBuf   :" + String(chBuf  ));
    DPRINTLN("jsonStr length:" + String(jsonStr.length()));
    DPRINTLN("chBuf   length:" + String(sizeof(chBuf   )));

    // Hashing JSON ??
    hashJSON(chBuf, sizeof(chBuf));
    rbase64.encode((char*)hmacResult);

    String resultHash = String(rbase64.result());
    DPRINTLN("Hash String: ");
    DPRINTLN(resultHash);

    String completeJSON = "{\"HMACRes\":\"" + resultHash + "\",\"Data\":" + jsonStr + "}";
    String payLoad      = "tag=DataESP&value=" + completeJSON;

    DPRINTLN("payload: ");
    DPRINTLN(payLoad);

    return payLoad;
  }

  bool sendJson()
  {
    String payLoad = buildJson();

    // Connexion to the host
    DPRINTLN("Connecting to ");
    DPRINTLN(host);

    if (!clientForGoogle.connect(host, port)){
      ERRORPRINTLN("Connection failed.");
      return false;
    }

    try{
      String postRequest =   "POST "  + String(uri)  + " HTTP/1.1\r\n" +
                            "Host: " + String(host) + "\r\n" +
                            "Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n" +
                        //  "Content-Type: application/json; utf-8\r\n" +
                            "Content-Length: " + payLoad.length() + "\r\n" + "\r\n" + payLoad;

      DPRINTLN("Post request: ");
      DPRINTLN(postRequest);

      // Sending the final string
      clientForGoogle.print(postRequest);
      clientForGoogle.stop();
      return true;
    }
    catch(int e){
      ERRORPRINT("Post request not succcessful");
      ERRORPRINT(e);
      return false;
    }
  }

  bool sendDataToGoogle()
  {
    // Verify the activation
    if (!B_GOOGLE_HTTPREQ){
      return false;
    }

    if (countForGoogleSend == N_GSHEETS){
      sendJson();
      countForGoogleSend = 0;
    }
    else{
      countForGoogleSend++;
    }
  }

#endif