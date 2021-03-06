#include "ArduinoMock.hpp"

ArduinoMock *ArduinoMock::instance = nullptr;

ArduinoMock &ArduinoMock::getInstance() {
    if (instance == nullptr)
        throw std::runtime_error("Error: no active ArduinoMock instance.");
    return *instance;
}
void ArduinoMock::begin() {
    if (instance != nullptr)
        throw std::runtime_error("Error: ArduinoMock instance already active.");
    instance = new ArduinoMock;
}
void ArduinoMock::end() {
    if (instance == nullptr)
        throw new std::runtime_error("Error: no acitve ArduinoMock instance.");
    delete instance;
    instance = nullptr;
}

SerialHelper &ArduinoMock::getSerial() {
    return getInstance().serial;
}