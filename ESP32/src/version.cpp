#include "version.h"

// TYPE = 0 (PROTOTYPE)
#if TYPE==0
  bool B_DEBUG_MODE = true;
  bool B_ANGLE_ADJUSTMENT = true;
  bool B_VCC_MNG = true;
  bool B_LIMITED_ANGLES = false;
  bool B_DISPLAY_ANGLES = true;
  bool B_DISPLAY_ACCEL = true;
  bool B_INHIB_NEG_VALS = false;
  bool B_INACTIVITY_ENABLE = false;
  bool B_GOOGLE_HTTPREQ = true;
  bool B_SERIALPORT = true;
  bool B_SERIALTELNET = true;
  bool B_OTA = true;
#endif

// TYPE = 1 (FINAL DELIVERY)
#if TYPE==1
  bool B_DEBUG_MODE = false;
  bool B_ANGLE_ADJUSTMENT = true;
  bool B_VCC_MNG = true;
  bool B_LIMITED_ANGLES = true;
  bool B_DISPLAY_ANGLES = false;
  bool B_DISPLAY_ACCEL = false;
  bool B_INHIB_NEG_VALS = true;
  bool B_INACTIVITY_ENABLE = true;
  bool B_SERIALPORT = BDEF_SERIALPORT;
  bool B_WIFI = true;
  bool B_WIFI_SMART_CONFIG = false;
  bool B_SERIALTELNET = false;
  bool B_GOOGLE_HTTPREQ = BDEF_GOOGLE_HTTPREQ;
  bool B_OTA = BDEF_OTA;
  bool B_BLE = BDEF_BLE;
#endif

// TYPE = 3 (PROTOTYPE-connectToWiFi)
#if TYPE==3
  bool B_DEBUG_MODE = true;
  bool B_ANGLE_ADJUSTMENT = false;
  bool B_VCC_MNG = true;
  bool B_LIMITED_ANGLES = false;
  bool B_DISPLAY_ANGLES = true;
  bool B_DISPLAY_ACCEL = true;
  bool B_INHIB_NEG_VALS = false;
  bool B_INACTIVITY_ENABLE = false;
  bool B_SERIALPORT = false;
  bool B_WIFI = true;
  bool B_WIFI_SMART_CONFIG = false;
#endif