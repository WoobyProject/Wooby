#include "HX711.h"
#include "version.h"
#include "bluetooth_com.h"
#include "main.h"

#ifdef BDEF_BLE
    #include "BluetoothSerial.h"
    BluetoothSerial SerialBT;
    bool BF_BLUETOOTH = false;
    bool BT_CLIENT_CONNECT = false;
#endif

#ifdef BDEF_BLE 

  void bluetoothCallback(esp_spp_cb_event_t event, esp_spp_cb_param_t *param)
  {
    if(event == ESP_SPP_SRV_OPEN_EVT)
    {
        Serial.println("Connection established");
        BT_CLIENT_CONNECT = true;
    }
    else if(event == ESP_SPP_CLOSE_EVT)
    {
        Serial.println("Connection closed");
        BT_CLIENT_CONNECT = false;
        ESP.restart();
    }
    /*
    else if(event == ESP_SPP_DATA_IND_EVT)
    {
        Serial.println("Data received");
        String response = bluetoothReadLine();
        if(response=="")
        {
            Serial.println("EMPTY");
        }
    }
    else if(event == ESP_SPP_WRITE_EVT)
    {
        Serial.println("Write operation complete");
    }
    */
  }
  
  bool setupBluetooth()
  {
    SerialBT.begin("Wooby", false); //Bluetooth device name
    BF_BLUETOOTH = false; // TODO !
    // SerialBT.register_callback(bluetoothCallback);

    return true;
  }

  void printSerialBluetooth()
  {
    if (BF_BLUETOOTH)
      return;

    if (!SerialBT.hasClient())
      return;
    
    // Sending the message via bluetooth
    SerialBT.print(genericJSONString);
    delay(50);
  }
#endif
