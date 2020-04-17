#include <AbsMouse.h>

const int ledPin = 13; // the pin that the LED is attached to
int incomingByte;      // a variable to read incoming serial data into
String inString = "";

void setup() {
  // initialize serial communication:
  Serial.begin(9600);
  // initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);
  AbsMouse.init(1920, 1080);
}

void loop() {
  // see if there's incoming serial data:
  if (Serial.available() > 0) {
    inString = Serial.readStringUntil(';');

     Serial.println("inString "+inString);
    // Declare the variables of the parts of the String
    String value1, value2;
     
    // For loop which will separate the String in parts
    // and assign them the the variables we declare
    for (int i = 0; i < inString.length(); i++) {
      if (inString.substring(i, i+1) == ",") {
        value1 = inString.substring(0, i);
        value2= inString.substring(i+1);
        break;
      }
    }
     
    // Sending the parts to Serial Monitor
    Serial.println(value1);
    Serial.println(value2);
    AbsMouse.move(value1.toInt(), value2.toInt());
    delay(200);
    AbsMouse.press(MOUSE_LEFT);
    delay(200);
    AbsMouse.release(MOUSE_LEFT);
  }
}