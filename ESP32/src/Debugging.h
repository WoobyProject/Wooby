// Variadic macros used to print information in de-bugging mode
// from LarryD, Arduino forum

#pragma once
// un-comment this line to print the debugging statements
#define DEBUGPRINT

#ifdef DEBUGPRINT
#define DPRINT(...) Serial.print(__VA_ARGS__)
#define DPRINTLN(...) ; Serial.println(__VA_ARGS__)
#else
#define DPRINT(...)
#define DPRINTLN(...)
#endif


// un-comment this line to print the debugging statements
// #define DEEPDEBUG

#ifdef DEEPDEBUG
  #define DEEPDPRINT(...)    Serial.print(__VA_ARGS__)
  #define DEEPDPRINTLN(...)  Serial.println(__VA_ARGS__)
#else
  // define blank line
  #define DEEPDPRINT(...)
  #define DEEPDPRINTLN(...)
#endif

// #define ERRORPRINT

#ifdef ERRORPRINT
  #define ERRORPRINT(...)    Serial.print(__VA_ARGS__)
  #define ERRORPRINTLN(...)  Serial.println(__VA_ARGS__)
#else
  // define blank line
  #define ERRORPRINT(...)
  #define ERRORPRINTLN(...)
#endif
