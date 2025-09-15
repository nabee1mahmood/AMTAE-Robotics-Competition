// Motor A
int ENA = 9;
int IN1 = 8;
int IN2 = 7;

// Motor B
int ENB = 3;
int IN3 = 5;
int IN4 = 4;

// Power level (0–255)
int power = 255;

void setup() {
  // Motor A pins
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // Motor B pins
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == 'F') {        // Both forward
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      analogWrite(ENA, power);

      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      analogWrite(ENB, power);

      Serial.println("Both Forward");
    } 
    else if (cmd == 'B') {   // Both backward
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      analogWrite(ENA, power);

      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
      analogWrite(ENB, power);

      Serial.println("Both Backward");
    } 
    else if (cmd == 'L') {   // Spin Left
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      analogWrite(ENA, power);

      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      analogWrite(ENB, power);

      Serial.println("Spin Left");
    } 
    else if (cmd == 'R') {   // Spin Right
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      analogWrite(ENA, power);

      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
      analogWrite(ENB, power);

      Serial.println("Spin Right");
    }
    else if (cmd == 'S') {   // Both stop
      analogWrite(ENA, 0);
      analogWrite(ENB, 0);

      Serial.println("Both Stop");
    }
  }
}
