#include <Arduino.h>
#include <SoftwareSerial.h>
#include "test.h"

SoftwareSerial serial(12, 13);

void setup() {
    serial.begin(9600);
}

void loop() {
    serial.println("Hello, world.");
    delay(get_delay());
}
