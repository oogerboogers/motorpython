#include <Arduino.h>
#define motorInterfaceType 1
#define enablePin 8
#define zDirPin 7
#define yDirPin 6
#define xDirPin 5
#define zStep 4
#define yStep 3
#define xStep 2
#define xLim 9
#define yLim 10
#define zLim 11

const int pulseWidth = 100;
const int stepsPerRevolution = 200; // Change this to fit the number of steps per revolution of your motor
const int queueSize = 50;

struct StepperMotor
{
  int directionPin;
  int stepPin;
  int limPin;
  int counter;
  int *queueDirections;
  int *queueSteps;
  int *queueIntervals;
  int *queueIds;
  int queueLength;
  int state;
  int limited;
};

int stepper_run(StepperMotor *motor, int delta)
{
  if (motor->queueLength == 0)
  {
    return -1;
  }

  motor->counter--;

  if (motor->counter > 0)
  {
    if (motor->state == HIGH && motor->counter <= motor->queueIntervals[0] / 2)
    {
      motor->state = LOW;
      digitalWrite(motor->stepPin, LOW);

      if (motor->queueSteps[0] <= 0)
      {
        motor->queueLength--;
        int id = motor->queueIds[0];
        for (int i = 0; i < motor->queueLength; i++)
        {
          motor->queueSteps[i] = motor->queueSteps[i + 1];
          motor->queueDirections[i] = motor->queueDirections[i + 1];
          motor->queueIntervals[i] = motor->queueIntervals[i + 1];
          motor->queueIds[i] = motor->queueIds[i + 1];
        }

        return id;
      }
    }
    return -1;
  }

  motor->counter += motor->queueIntervals[0];

  if (motor->queueIds[0] == 0 && digitalRead(motor->limPin) == 0) {
    motor->queueLength = 0;
    return -2;
  }

  motor->state = HIGH;
  
  if (motor->queueSteps[0] > 0)
  {
    digitalWrite(motor->directionPin, motor->queueDirections[0]);
    digitalWrite(motor->stepPin, HIGH);
  }
  motor->queueSteps[0]--;
  return -1;
}

StepperMotor createMotor(int directionPin, int stepPin, int limPin)
{
  StepperMotor motor = {
      directionPin,
      stepPin,
      limPin,
      0,
      new int[queueSize],
      new int[queueSize],
      new int[queueSize],
      new int[queueSize],
      0,
      0,
      -1
    };

  return motor;
}

void initMotor(StepperMotor *motor)
{
  pinMode(motor->directionPin, OUTPUT);
  pinMode(motor->stepPin, OUTPUT);
  pinMode(motor->limPin, INPUT_PULLUP);
  digitalWrite(motor->directionPin, LOW);
  digitalWrite(motor->stepPin, LOW);
}

int queueAction(StepperMotor *motor, int direction, int stepCount, int interval, int id)
{
  int queueLen = motor->queueLength;
  if (queueLen >= queueSize)
  {
    return 0;
  }

  motor->queueSteps[queueLen] = stepCount;
  motor->queueDirections[queueLen] = direction;
  motor->queueIntervals[queueLen] = interval;
  motor->queueIds[queueLen] = id;
  motor->queueLength++;
  return 1;
}

StepperMotor motorX = createMotor(xDirPin, xStep, xLim);
StepperMotor motorY = createMotor(yDirPin, yStep, yLim);
StepperMotor motorZ = createMotor(zDirPin, zStep, zLim);

void setup()
{
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, LOW);
  initMotor(&motorX);
  initMotor(&motorY);
  initMotor(&motorZ);
  Serial.begin(9600);
  Serial.print("r");
  Serial.print("\n");
}

unsigned long lastTime = 0;

void loop()
{

  if (Serial.available() > 0)
  {
    char type = Serial.read();
    if (type == 'a')
    {
      int count = Serial.parseInt();
      int direction = Serial.parseInt();
      int interval = Serial.parseInt();
      int id = Serial.parseInt();
      int motorID = Serial.parseInt();
      StepperMotor *motor = &((motorID == 0) ? motorX : (motorID == 1 ? motorY : motorZ));

      int result = queueAction(motor, direction, count, interval, id);

      Serial.print("c");
      Serial.print(result);
      Serial.print("\n");
    }
    else
    {
      Serial.print("f");
      Serial.print("\n");
    }
  }

  unsigned long newTime = micros();
  unsigned long deltaL = newTime - lastTime;
  lastTime = newTime;
  int delta = (int)deltaL;

  int doneId = stepper_run(&motorX, delta);
  if (doneId != -1)
  {
    Serial.print("x");
    Serial.print(doneId);
    Serial.print("\n");
  }

  doneId = stepper_run(&motorY, delta);
  if (doneId != -1)
  {
    Serial.print("y");
    Serial.print(doneId);
    Serial.print("\n");
  }

  doneId = stepper_run(&motorZ, delta);
  if (doneId != -1)
  {
    Serial.print("z");
    Serial.print(doneId);
    Serial.print("\n");
  }
}
