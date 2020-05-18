#define LED 2
#define BUTTON 7
#define START 3

// Using http://slides.justen.eng.br/python-e-arduino as refference
int buttonState = 0;         // variable for reading the pushbutton status

void setup() {
    pinMode(LED, OUTPUT);
    pinMode(BUTTON, INPUT);
    pinMode(START, OUTPUT);
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
    digitalWrite(START, HIGH);
  } else {
    // turn LED off:
    digitalWrite(START, LOW);
  }
}
