
#define trigPin1 9 
#define echoPin1 10 
#define LED_first_ping 22
int incomingByte = 0; 
#define trigPin2 3
#define echoPin2 11
#define LED_second_ping 24

long duration, distance, UltraSensor1, UltraSensor2, constrainedDuration;
char data;

void setup()
{ 
        Serial.begin(9600);
        pinMode(trigPin1, OUTPUT);
        pinMode(echoPin1, INPUT);
        pinMode(trigPin2, OUTPUT);
        pinMode(echoPin2, INPUT);
} 


void loop() 
{  
        
                SonarSensor(trigPin1, echoPin1);
                UltraSensor1 = distance; 
                SonarSensor(trigPin2, echoPin2);
                UltraSensor2 = distance;                          
                if(UltraSensor1 > UltraSensor2)
                        
                {                   
                  Serial.println("1");
                }
               else if (UltraSensor2 > UltraSensor1)
                {
                  Serial.println("2");
                }
               else if(UltraSensor2 == UltraSensor1 && UltraSensor1 == UltraSensor2)
               {
                 Serial.println("3");                 
               }
                delay(300);           
   }
    
void SonarSensor(int trigPinSensor, int echoPinSensor) 
    {
        digitalWrite(trigPinSensor, LOW);  
        delayMicroseconds(2); 
        digitalWrite(trigPinSensor, HIGH); 
        delayMicroseconds(10); 
        digitalWrite(trigPinSensor, LOW); 
       
        duration = pulseIn(echoPinSensor, HIGH); 
        distance = (duration / 2) / 29.1;
    }

  

