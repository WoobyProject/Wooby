//***** WIFI CONF *****//

#define N_GSHEETS 5
#define WLAN_HOSTNAME   "Wooby"

extern bool BF_WIFI;

extern bool checkWiFiConnection();
extern bool setupWiFi();
extern String getIp();
#if B_GOOGLE_HTTPREQ == true
  extern const char *host;
  // const char  *GScriptId = "AKfycbzATY3EipQ9N2ups-5LlyD91IbE4rKa1A-9CkzC1LkojDGyA1A"; // within Sheets
  // const char  *GScriptId = "AKfycbwdvWUgeXTPaf5jsUKoXcOWmwSjmpGaRcV5KfeoOb1AvQyvByKU"; // stand-alone
  // const char  *GScriptId =  "AKfycbxWW4T3xRrYyCOoCITc_TU-0rHeqsBjNKPtWjvBoOvgGvzAMXaU"; // StoreI within Sheets
  extern const char *GScriptId; // Wooby within Sheets
  extern const String uri;
  extern const int port;
  extern const char* root_ca;

  extern WiFiClientSecure clientForGoogle;
  extern unsigned long countForGoogleSend;
  extern bool BF_GOOGLE_HTTPREQ;
  extern StaticJsonDocument<1000> dataItem;                         // Memory for the JSON tree  ATTENTION:Increase the memory if needded

  //***** ENCRYPTION CONF *****//
  extern SHA256 sha;
  extern RTC_DATA_ATTR const char *key;   // NOT SAFE KEY IN CLEAR!!!!!!!!!!!!!!!!!!!!!!!!!!
  extern byte hmacResult[];
#endif