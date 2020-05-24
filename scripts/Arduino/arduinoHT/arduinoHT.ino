#define LED 2
#define BUTTON 3

// Using http://slides.justen.eng.br/python-e-arduino as refference
// https://stackoverflow.com/questions/54662362/sending-signal-from-arduino-serial-to-a-python-program
int buttonState = 0;         // variable for reading the pushbutton status

void setup() {
    pinMode(LED, OUTPUT);
    pinMode(BUTTON, INPUT);
    Serial.begin(9600);
}

void loop() {
    if (Serial.available()) {
        char serialListener = Serial.read();
        if (serialListener == 'H') {
            digitalWrite(LED, HIGH);
        }
        else if (serialListener == 'L') {
            digitalWrite(LED, LOW);
        }
    }
    buttonState = digitalRead(BUTTON);
    if (buttonState == HIGH) {
      Serial.println('1');
      delay(100);
    }
}
