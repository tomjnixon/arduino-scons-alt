#include <Arduino.h>

int led = 13;

void setup() {
    pinMode(led, OUTPUT);
}

void loop() {
    digitalWrite(led, HIGH);
    delay(DELAY);
    digitalWrite(led, LOW);
    delay(DELAY);
}
