    
int channel [256]; 

const int CLKpin = A1;
const int SIpin = A2;
const int AOpin = A0;
int LED = 12;
int UV = 8; 


// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(CLKpin, OUTPUT);
  pinMode(SIpin, OUTPUT);
  pinMode(LED,OUTPUT);
  pinMode(UV,OUTPUT);
  Serial.begin(9600);  
}

void readSensor() {
  //for (int x = 0; x < 100; x++) {
  //  PORTC = PORTC | 0x02;  // turn the CLK on (HIGH is the voltage level)
    //delayMicroseconds(1);
  //  PORTC = PORTC & ~0x02;  // turn the CLK off by making the voltage LOW
    //delayMicroseconds(1);
  //}
  
  PORTC |= 0x04; // set SI
  //delayMicroseconds(1);
  PORTC |= 0x02; //set CLK 
  //delayMicroseconds(1);
  PORTC &= ~0x04; // reset SI
  //delayMicroseconds(1);
  PORTC &= ~0x02; // reset CLK  
  //delayMicroseconds(1);

  for (int x = 0; x < 256; x++) {
    //delayMicroseconds(1);
    channel[x] = analogRead(A0);
    PORTC = PORTC | 0x02;  // turn the CLK on (HIGH is the voltage level)
    //delayMicroseconds(2);
    PORTC = PORTC & ~0x02;  // turn the CLK off by making the voltage LOW
    //delayMicroseconds(2);
  }

}

// the loop function runs over and over again forever
void loop() {
  static int exposure = 1;
  
  while(Serial.available() == 0);
  char command = Serial.read();
/*  int val = Serial.parseInt(); 
  if (isDigit(thisChar)) {
      Serial.println(val);;
    }
    */

  switch(command) {
    case 'U':
      digitalWrite(UV, HIGH);
      break;
    case 'V':
      digitalWrite(UV,LOW);
      break;
    case 'X':
     digitalWrite(LED, LOW);
     break;
    case 'Y':
     digitalWrite(LED, HIGH);
     break;
    case 'A':
      exposure = 1;
      break;
    case 'B':
      exposure = 10;
      break;
    case 'C': 
      exposure = 30;
      break;
    case 'D':
      exposure = 500;
      break;
    case 'E': 
      exposure = 700;
      break;
    case 'R':
      readSensor();
      delay(exposure);
      readSensor();
      Serial.print("Exposure: ");
      Serial.println(exposure);
      for (int x = 0; x <256; ++x) {
        Serial.print(x);
        Serial.print(',');
        Serial.println(channel[x]);
      }   
  }
  /*
  readSensor();
  delay(1);
  readSensor();
  for (int x = 0; x <256; ++x) {
    Serial.print(x);
    Serial.print(',');
    Serial.println(channel[x]);
  }
 */
}






