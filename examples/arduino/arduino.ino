// ----------------- Motor Pins -----------------
// Motor A (Left)
int ENA = 9;
int IN1 = 8;
int IN2 = 7;

// Motor B (Right)
int ENB = 3;
int IN3 = 5;
int IN4 = 4;

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.begin(9600);
  Serial.setTimeout(50);
}

// Drive one motor with signed speed
// spd = -100..100
void driveMotor(int EN, int INa, int INb, int spd) {
  int pwm = map(abs(spd), 0, 100, 0, 255);
  if (spd > 0) {        // forward
    digitalWrite(INa, HIGH);
    digitalWrite(INb, LOW);
    analogWrite(EN, pwm);
  } else if (spd < 0) { // backward
    digitalWrite(INa, LOW);
    digitalWrite(INb, HIGH);
    analogWrite(EN, pwm);
  } else {              // stop
    analogWrite(EN, 0);
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() == 0) return;

    // Expect: "L,-75,80" (Left=-75%, Right=+80%)
    int comma1 = input.indexOf(',');
    int comma2 = input.indexOf(',', comma1 + 1);

    int leftSpd  = input.substring(0, comma1).toInt();
    int rightSpd = input.substring(comma1 + 1, comma2).toInt();

    driveMotor(ENA, IN1, IN2, leftSpd);
    driveMotor(ENB, IN3, IN4, rightSpd);

    Serial.print("Left=");  Serial.print(leftSpd);
    Serial.print(" Right="); Serial.println(rightSpd);
  }
}
