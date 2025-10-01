// ----------------- Motor Pins -----------------
// Motor A (Left)
int ENA = 9;
int IN1 = 8;
int IN2 = 7;

// Motor B (Right)
int ENB = 3;
int IN3 = 5;
int IN4 = 4;

// ----------------- Control Vars -----------------
unsigned long lastCommandTime = 0;   // track last valid command
int leftSpd = 0;
int rightSpd = 0;

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.begin(9600);
  Serial.setTimeout(50);

  // start with motors off
  driveMotor(ENA, IN1, IN2, 0);
  driveMotor(ENB, IN3, IN4, 0);
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
  // --------- Check Serial for New Commands ---------
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      int comma = input.indexOf(',');
      if (comma > 0) {
        leftSpd  = input.substring(0, comma).toInt();
        rightSpd = input.substring(comma + 1).toInt();
      }

      lastCommandTime = millis(); // update watchdog
    }
  }

  // --------- Watchdog Failsafe ---------
  if (millis() - lastCommandTime > 500) { // >0.5 sec no command
    leftSpd = 0;
    rightSpd = 0;
  }

  // --------- Drive Motors ---------
  driveMotor(ENA, IN1, IN2, leftSpd);
  driveMotor(ENB, IN3, IN4, rightSpd);
}
