//***** WIFI CONF *****//

bool BF_WIFI = true;

#define WLAN_HOSTNAME   "Wooby"
#define WLAN_MAX_COUNT  7
/*
#define WLAN_LIB_N      4
String WLAN_NAME_LIB[]  = {"Wooby" ,        "Kike's House"        , "Jose's House",   "Adris's House"};
String WLAN_SSID_LIB[]  = {"Wooby"     ,    "SFR_6608"            , "SFR-5538",       "Livebox-1D06"};
String WLAN_PASS_LIB[]  = {"TonsOfSmiles" , "2cwt45yriv2urm57trbx", "VHYWP9A2PVDU",   "bFnRC5bEUkGKmxydKx"};
*/

#define WLAN_LIB_N      1
String WLAN_NAME_LIB[]  = {"Wooby" };
String WLAN_SSID_LIB[]  = {"Wooby"   };
String WLAN_PASS_LIB[]  = {"TonsOfSmiles"};


int count = 0;
const int N_GSHEETS = 5;

char bufIp[] = "192.168.000.000";

//***** FUNCTIONS SOFT ACCESS POINT *****//

const char* ssidAP = "Wooby";
const char* passwordAP = "tonsofsmiles";
IPAddress IP_AP;


bool BF_SOFTAP = true;

bool setupSoftAP(){

  BF_SOFTAP = !WiFi.softAP(ssidAP, passwordAP);

  if (BF_SOFTAP){
    Serial.printf("\n\tSoft Access Point setup NOT succesful !\n\n");
    return false;
  }

  IP_AP  = WiFi.softAPIP();
  Serial.print("url: http://");
  Serial.print(IP_AP);

  return true;

}


//***** FUNCTIONS *****//

bool checkWiFiConnection(){
  return (WiFi.status()==WL_CONNECTED);
}

bool WiFiConnectFromLib() {

  // Setting host name ...
  WiFi.setHostname(WLAN_HOSTNAME);

  // For every WiFi network in the library...
  for(int i=0; i<WLAN_LIB_N; i++){
    // char* currentWLAN_SSID;

    WiFi.begin(WLAN_SSID_LIB[i].c_str(), WLAN_PASS_LIB[i].c_str());

    Serial.print("Trying to connect to ");
    Serial.print(WLAN_NAME_LIB[i]);
    Serial.print(" (");
    Serial.print(WLAN_SSID_LIB[i]);
    Serial.println(")");

    int counter = 0;
    while (WiFi.status() != WL_CONNECTED && counter < WLAN_MAX_COUNT) {
      delay(200);
      Serial.print(".");
      counter++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED){
      Serial.print("WiFi connected after ");
      Serial.print(counter);
      Serial.println(" attempts");
      Serial.println("IP address: ");
      Serial.println(WiFi.localIP());
      Serial.println("GatewayIP address: ");
      Serial.println(WiFi.gatewayIP());
      Serial.println("");
      return true;
    }
    else{
      Serial.println("Failed to connect to ");
      Serial.print(WLAN_NAME_LIB[i]);
      Serial.print(" (");
      Serial.print(WLAN_SSID_LIB[i]);
      Serial.println(")");
    }
  }

  Serial.println("No successful connection AT ALL!! ");
  return false;
}

bool WiFiConnectSmartConfig(){

  WiFi.mode(WIFI_AP_STA);
  /* Start SmartConfig */
  WiFi.beginSmartConfig();

  /* Wait for SmartConfig packet from mobile */
  Serial.println("Waiting for SmartConfig.");
  while (!WiFi.smartConfigDone()) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("SmartConfig done.");

  /* Wait for WiFi to connect to AP */
  // TODO ! This is blocking! Create a counter !
  Serial.println("Waiting for WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  return true;
}

bool setupWiFi (){
  if (!BDEF_WIFI){
    return false;
  }

  if (!B_WIFI){
    Serial.printf("\tWiFI has been deactivated\n");
    WiFi.disconnect();
    WiFi.mode(WIFI_OFF);
    return false;
  }
  
  WiFi.mode(WIFI_STA);

  // Setting up the WiFi (for real) //
  if (B_WIFI_SMART_CONFIG){
    WiFiConnectSmartConfig();
  }
  else{
    WiFiConnectFromLib();
  }
  delay(50);

  Serial.printf("\n\n");
  Serial.printf("From WiFi we have %d\n", WiFi.begin()==WL_CONNECTED);
  Serial.printf("From function we have %d\n", checkWiFiConnection());
  

  return checkWiFiConnection();

}

String ip2String(IPAddress ip){
  char ipstr[20];
  sprintf(ipstr, "%d.%d.%d.%d", ip[0],ip[1],ip[2],ip[3]);
  return String(ipstr);
}

String getIp(){
  return ip2String(WiFi.localIP());
}

//***** GOOGLE CONF *****//

#if B_GOOGLE_HTTPREQ == true
  WiFiClientSecure clientForGoogle;

  unsigned long countForGoogleSend = 0;
  bool BF_GOOGLE_HTTPREQ = false;

  static const int   JSONSiz       =  1000;
  StaticJsonDocument<JSONSiz> dataItem;                         // Memory for the JSON tree  ATTENTION:Increase the memory if needded


  const char  *host      = "script.google.com";
  // const char  *GScriptId = "AKfycbzATY3EipQ9N2ups-5LlyD91IbE4rKa1A-9CkzC1LkojDGyA1A"; // within Sheets
  // const char  *GScriptId = "AKfycbwdvWUgeXTPaf5jsUKoXcOWmwSjmpGaRcV5KfeoOb1AvQyvByKU"; // stand-alone
  // const char  *GScriptId =  "AKfycbxWW4T3xRrYyCOoCITc_TU-0rHeqsBjNKPtWjvBoOvgGvzAMXaU"; // StoreI within Sheets
  const char  *GScriptId = "AKfycbzATY3EipQ9N2ups-5LlyD91IbE4rKa1A-9CkzC1LkojDGyA1A"; // Wooby within Sheets

  const String uri       = String("/macros/s/") + String(GScriptId) + String("/exec?");

  const int port   = 443;

  const char* root_ca = \
  "-----BEGIN CERTIFICATE-----\n" \
  "MIIESjCCAzKgAwIBAgINAeO0mqGNiqmBJWlQuDANBgkqhkiG9w0BAQsFADBMMSAw\n" \
  "HgYDVQQLExdHbG9iYWxTaWduIFJvb3QgQ0EgLSBSMjETMBEGA1UEChMKR2xvYmFs\n" \
  "U2lnbjETMBEGA1UEAxMKR2xvYmFsU2lnbjAeFw0xNzA2MTUwMDAwNDJaFw0yMTEy\n" \
  "MTUwMDAwNDJaMEIxCzAJBgNVBAYTAlVTMR4wHAYDVQQKExVHb29nbGUgVHJ1c3Qg\n" \
  "U2VydmljZXMxEzARBgNVBAMTCkdUUyBDQSAxTzEwggEiMA0GCSqGSIb3DQEBAQUA\n" \
  "A4IBDwAwggEKAoIBAQDQGM9F1IvN05zkQO9+tN1pIRvJzzyOTHW5DzEZhD2ePCnv\n" \
  "UA0Qk28FgICfKqC9EksC4T2fWBYk/jCfC3R3VZMdS/dN4ZKCEPZRrAzDsiKUDzRr\n" \
  "mBBJ5wudgzndIMYcLe/RGGFl5yODIKgjEv/SJH/UL+dEaltN11BmsK+eQmMF++Ac\n" \
  "xGNhr59qM/9il71I2dN8FGfcddwuaej4bXhp0LcQBbjxMcI7JP0aM3T4I+DsaxmK\n" \
  "FsbjzaTNC9uzpFlgOIg7rR25xoynUxv8vNmkq7zdPGHXkxWY7oG9j+JkRyBABk7X\n" \
  "rJfoucBZEqFJJSPk7XA0LKW0Y3z5oz2D0c1tJKwHAgMBAAGjggEzMIIBLzAOBgNV\n" \
  "HQ8BAf8EBAMCAYYwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMBIGA1Ud\n" \
  "EwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYEFJjR+G4Q68+b7GCfGJAboOt9Cf0rMB8G\n" \
  "A1UdIwQYMBaAFJviB1dnHB7AagbeWbSaLd/cGYYuMDUGCCsGAQUFBwEBBCkwJzAl\n" \
  "BggrBgEFBQcwAYYZaHR0cDovL29jc3AucGtpLmdvb2cvZ3NyMjAyBgNVHR8EKzAp\n" \
  "MCegJaAjhiFodHRwOi8vY3JsLnBraS5nb29nL2dzcjIvZ3NyMi5jcmwwPwYDVR0g\n" \
  "BDgwNjA0BgZngQwBAgIwKjAoBggrBgEFBQcCARYcaHR0cHM6Ly9wa2kuZ29vZy9y\n" \
  "ZXBvc2l0b3J5LzANBgkqhkiG9w0BAQsFAAOCAQEAGoA+Nnn78y6pRjd9XlQWNa7H\n" \
  "TgiZ/r3RNGkmUmYHPQq6Scti9PEajvwRT2iWTHQr02fesqOqBY2ETUwgZQ+lltoN\n" \
  "FvhsO9tvBCOIazpswWC9aJ9xju4tWDQH8NVU6YZZ/XteDSGU9YzJqPjY8q3MDxrz\n" \
  "mqepBCf5o8mw/wJ4a2G6xzUr6Fb6T8McDO22PLRL6u3M4Tzs3A2M1j6bykJYi8wW\n" \
  "IRdAvKLWZu/axBVbzYmqmwkm5zLSDW5nIAJbELCQCZwMH56t2Dvqofxs6BBcCFIZ\n" \
  "USpxu6x6td0V7SvJCCosirSmIatj/9dSSVDQibet8q/7UK4v4ZUN80atnZz1yg==\n" \
  "-----END CERTIFICATE-----\n";


  //***** ENCRYPTION CONF *****//
  SHA256                             sha;
  RTC_DATA_ATTR const char       *key            = "i3ozue5rg2ha7zer96thzht";   // NOT SAFE KEY IN CLEAR!!!!!!!!!!!!!!!!!!!!!!!!!!

  byte hmacResult[32];

#endif