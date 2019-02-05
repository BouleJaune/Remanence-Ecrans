#include <FlexiTimer2.h>


    int photocellPin = 0;     
    int photocellReading;     
    byte lb;
    byte hb;
    
    void setup(void) {
      
      Serial.begin(115200);
      FlexiTimer2::set(1,1.0/2000, Mesure); 
      FlexiTimer2::start(); 
    }
     
    void loop(void) {
      
    }

    void Mesure() {
      photocellReading = analogRead(photocellPin);   
      // Serial.write(photocellPin);  
      lb=lowByte(photocellReading);
      hb=highByte(photocellReading);
      Serial.write(lb);
      Serial.write(hb);       
    }

