#include <IRremote.h>

IRrecv recv(2);
IRsend IrSender;

int IRSenderPin = 3;
int onPin = 12;
int offPin = 11;

void setup() {
  recv.enableIRIn();
  Serial.begin(9600);
  IrSender.begin(IRSenderPin, 13);
  pinMode(onPin, INPUT_PULLUP);
  pinMode(offPin, INPUT_PULLUP);
}

void loop() {
  // Empfangene IR-Signale dekodieren und anzeigen
  if (recv.decode()) {
    Serial.println(recv.decodedIRData.decodedRawData, HEX);
    recv.printIRResultShort(&Serial);
    recv.resume();
  }

  // IR-Signal senden, wenn der Knopf gedrückt wird
  if (digitalRead(onPin) == LOW) {
    IrSender.sendNEC(0xEF00, 0x3, 5);
    delay(1000);  // Anti-Bounce-Delay
  }

  if (digitalRead(offPin) == LOW) {
    IrSender.sendNEC(0xEF00, 0x2, 2);
    delay(1000);  // Anti-Bounce-Delay
  }

  delay(20);  // Allgemeines Delay zur Entlastung des Mikrocontrollers
}
