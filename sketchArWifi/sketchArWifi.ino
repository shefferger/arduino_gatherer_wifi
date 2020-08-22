int d_1 = 0;
int d_2 = 1;

String pass = "E209229";            
String ID = "0042";                
String detector1 = "potentiometr_1";
String detector2 = "potentiometr_2";

bool isConnected = false;           
String inChar;
String req;

void setup() {
  Serial.begin(115200); 
}


void loop() {
  delay(50);
  if (Serial.available() > 0) {   
    inChar = Serial.readString(); 
    if (!isConnected){            
      if (inChar == "search"){   
        Serial.print("imArduino");
      }
      if (inChar == pass){        
        isConnected = true;      
        Serial.print("ok\n");          
        delay(100);
        }
    } 
  }  
  else{
    if (isConnected){
      delay(100);
      Serial.print("=" + ID);
      Serial.print("=" + detector1);
      Serial.print("=" + String(analogRead(d_1)) + ";");
      delay(100);
      Serial.print("=" + ID);
      Serial.print("=" + detector2);
      Serial.print("=" + String(analogRead(d_2)) + ";");
      delay(300);
      }
  }
}
