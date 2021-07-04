#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "version.h"
#include "telnet_com.h"

#if B_SERIALTELNET==true
  #define MAX_SRV_CLIENTS 1
  WiFiServer serverTelnet(23);
  WiFiClient serverTelnetClients[MAX_SRV_CLIENTS];
  bool BF_SERIALTELNET = false;
  int nTelnetClients = 0;
#endif

#ifdef B_SERIALTELNET

  bool setupTelnet()
  {
    if (!B_SERIALTELNET){
      Serial.print("WARNING: Telnet is is turned off. Telnet won't work");
      return false;
    }

    // Verifying WiFi connection
    if (!B_WIFI){
      Serial.print("WARNING: WiFi is turned off. Telnet won't work");
      return false;
    }
    BF_WIFI = !checkWiFiConnection();
    if (BF_WIFI){
      Serial.printf("\nWARNING: WiFi failed. Telnet won't work.");
      return false;
    }

    serverTelnet.begin();
    serverTelnet.setNoDelay(true);
    Serial.print("Ready to use Telnet ");
    Serial.println(WiFi.localIP());
    return true;
  }

  bool checkTelnetClients()
  {
    int i; // Correction TO DO! A variable should keep track of the numnber of clientes

    // Check for new clients
    if (serverTelnet.hasClient()) {
      Serial.printf("\nNew client request!\n");
      for(i = 0; i < MAX_SRV_CLIENTS; i++){
          //find free/disconnected spot
          if (!serverTelnetClients[i] || !serverTelnetClients[i].connected()){
            if(serverTelnetClients[i]) serverTelnetClients[i].stop();
            serverTelnetClients[i] = serverTelnet.available();
            if (!serverTelnetClients[i]){Serial.println("Client communication broken");}
            Serial.printf("\nNew telnet client(%d) \n", i);
            Serial.println(serverTelnetClients[i].remoteIP());
            nTelnetClients++;
            break;
          }
      }
      if (i >= MAX_SRV_CLIENTS) {
          //no free/disconnected spot so reject
          Serial.printf("\nWARNING: Maximum of telnet clients reached!\n");
          serverTelnet.available().stop();
      }

    }

    for(i = 0; i < MAX_SRV_CLIENTS; i++){
      // if (serverTelnetClients[i].connected())
        //Serial.printf("\nClient %d - Connected: %d -  IP: %s \n", i, serverTelnetClients[i].connected(), ip2String(serverTelnetClients[i].remoteIP()).c_str() );
    }

    return true;

  }

  void printSerialTelnet()
  {
  if (!B_SERIALTELNET)
    return;

  checkTelnetClients();

  // DPRINTF("\nLength minified JSON: \t%d", measureJson(genericJSON));
  // DPRINTF("\nLength prettified JSON: \t%d\n", measureJsonPretty(genericJSON));
  for(int i = 0; i < MAX_SRV_CLIENTS; i++){
    if (serverTelnetClients[i] && serverTelnetClients[i].connected()){
      serverTelnetClients[i].print("WT");
      String output;
      serializeJson(genericJSON, output);
      serverTelnetClients[i].print(output);
      // serializeJson(genericJSON, serverTelnetClients[i]); //serializeJsonPretty
      // serverTelnetClients[i].printf("\n"); Unnecessary, the message already has a /r/n at the end
      delay(100);
    }
  }
}

#endif