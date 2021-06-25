#define MODEL 1
// MODEL 1 : ESP32 - Wooby 1
// MODEL 2 : ESP32 - Wooby 2
// MODEL 3 : Arduino - Unknown
// MODEL 4 : Arduino - Unknown
// MODEL 5 : ESP32 - Wooby Xtrem

#define TYPE 1

// TYPE = 0 (PROTOTYPE)
#if TYPE==0
  extern bool B_DEBUG_MODE;
  extern bool B_ANGLE_ADJUSTMENT;
  extern bool B_VCC_MNG;
  extern bool B_LIMITED_ANGLESe;
  extern bool B_DISPLAY_ANGLES;
  extern bool B_DISPLAY_ACCEL;
  extern bool B_INHIB_NEG_VALS;
  extern bool B_INACTIVITY_ENABLE;
  extern bool B_SERIALPORT;
  extern bool B_SERIALTELNET;
  extern bool B_GOOGLE_HTTPREQ;
  extern bool B_OTA;
#endif

// TYPE = 1 (FINAL DELIVERY)
#if TYPE==1
  #define BDEF_SERIALPORT true
  #define BDEF_GOOGLE_HTTPREQ true
  #define BDEF_OTA true
  #define BDEF_BLE true
  extern bool B_DEBUG_MODE;
  extern bool B_ANGLE_ADJUSTMENT;
  extern bool B_VCC_MNG;
  extern bool B_LIMITED_ANGLES;
  extern bool B_DISPLAY_ANGLES;
  extern bool B_DISPLAY_ACCEL;
  extern bool B_INHIB_NEG_VALS;
  extern bool B_INACTIVITY_ENABLE;
  extern bool B_SERIALPORT;
  extern bool B_WIFI;
  extern bool B_WIFI_SMART_CONFIG;
  extern bool B_SERIALTELNET;
  extern bool B_GOOGLE_HTTPREQ;
  extern bool B_OTA;
  extern bool B_BLE;
#endif

// TYPE = 3 (PROTOTYPE-connectToWiFi)
#if TYPE==3
  #define B_SERIALTELNET true 
  #define B_GOOGLE_HTTPREQ false
  #define B_OTA true
  #define B_BLE true 
  extern bool B_DEBUG_MODE;
  extern bool B_ANGLE_ADJUSTMENT;
  extern bool B_VCC_MNG;
  extern bool B_LIMITED_ANGLES;
  extern bool B_DISPLAY_ANGLES;
  extern bool B_DISPLAY_ACCEL;
  extern bool B_INHIB_NEG_VALS;
  extern bool B_INACTIVITY_ENABLE;
  extern bool B_SERIALPORT;
  extern bool B_WIFI;
  extern bool B_WIFI_SMART_CONFIG;
#endif