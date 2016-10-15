#include <SPI.h>
#include <mcp4xxx.h>

using namespace icecave::arduino;

#define POTENTIOMETER_PIN 10
#define FEEDBACK_PIN A0 

#define ERROR_LED_PIN 5
#define TDCS_LED_PIN 4
#define ON_LED_PIN 3

const double extra_R = 3; 
const double R_W = 70 + extra_R; // Min potentiometer resistance
const double R_S = 10000/256; // Potentiometer step


// Data
MCP4XXX* pot;
double voltage;
double potentiometer_resistance;
double return_resistance;
double current;
double target_current;
bool is_connected;
bool on_led_status;
bool do_tdcs;
int pot_status;

void set_potentiometer(int value)
/*
 * Sets the resistance of the potentiometer (0...255)
 * 0 -> 70 Ohm
 * 255 0 -> 10070 Ohn
 */
{
  if (value < 0)
    value = 0;
  if (value > 255)
    value = 255;
    
  pot_status = value;
  pot->set(value);
  potentiometer_resistance = value*R_S + R_W;  
  
}

void calculate_status()
/**
 * Calculates the voltage drop across the potentiometer, the output current and the output resistance
 */
{
  // Voltage drop across the potentiometer
  voltage = 5 - analogRead(FEEDBACK_PIN)*5.0/1024.0;
  // Current going through the potentiometer
  current = voltage/double(potentiometer_resistance);
  // Connected 
  return_resistance = (5 - voltage) / current;
}

double my_abs(double a){
  return a>0?a:-a;    
}

void adjust_current(int times, int sleep)
/*
 * Adjust potentiometer to match target current
 * times: number of times to adjust the potentiometer
 * sleep: ms to sleep between each adjustment
 */
{
  for (int i = 0;i<times;i++)
  {
    calculate_status();
  
    if (do_tdcs){
  
      // Short circuit protection
      if (current > 0.005)
      {
        set_potentiometer(255);    
      }
      else if (current > target_current && my_abs(current-target_current)>0.0001 )
      {
        //While we are over the target current,  increase the resistance      
        pot_status++;
        set_potentiometer(pot_status);
      }
      else if (current < target_current  && my_abs(current-target_current)>0.0001)
      {
        //While we are under the target current, decrase the resistance
        pot_status--;
        set_potentiometer(pot_status);      
      }
    }
   delay(sleep);
  }
}



void setup()
{
  digitalWrite(TDCS_LED_PIN, HIGH);
  digitalWrite(ON_LED_PIN, HIGH);
  digitalWrite(ERROR_LED_PIN, HIGH);
  
  Serial.begin(9600); 
  pot = new MCP4XXX(POTENTIOMETER_PIN);
  set_potentiometer(255);
  target_current = 0;
  do_tdcs = 0;
  is_connected = 0;
  on_led_status = 1;

  pinMode(ERROR_LED_PIN, OUTPUT);
  pinMode(TDCS_LED_PIN, OUTPUT);
  pinMode(ON_LED_PIN, OUTPUT);
  digitalWrite(ERROR_LED_PIN, LOW);
  digitalWrite(TDCS_LED_PIN, LOW);
  digitalWrite(ON_LED_PIN, HIGH);

}

#define HANDSHAKE_CODE 512
#define START 127
#define STOP 128
#define START_HARSH 130
#define STOP_HARSH 131
#define QUERY 129
#define SET_LOW 1024
#define SET_HIGH 2048

void loop()
{

  // Step 1: Flash the status led and check for incoming connections
  while(!is_connected)
  {
    delay(300);
    if (on_led_status)
    {
      digitalWrite(ON_LED_PIN, LOW);
      on_led_status = 0;
    }
    else
    {
      digitalWrite(ON_LED_PIN, HIGH);
      on_led_status = 1;
    }
    
    if (Serial.available() > 0) 
    {
      int code = Serial.parseInt();
      if (code == HANDSHAKE_CODE)
      {
        Serial.println("OK");
        is_connected = 1;
        digitalWrite(ERROR_LED_PIN, LOW);
        digitalWrite(ON_LED_PIN, HIGH);
      }
      else
      {  
        digitalWrite(ERROR_LED_PIN, HIGH);        
      }
    }
   
  }
 
  // Calculates the current status and adjusts potentiometer (if tDCS is active)
  calculate_status();
  // Run 15 adjust itereations
  if (do_tdcs)
      adjust_current(10, 5);
  
  // Parse the next command
  if (Serial.available() > 0) {
    
    int code = Serial.parseInt();
    if (code == START)
    {
      do_tdcs = 1;
      adjust_current(255, 4);
      digitalWrite(TDCS_LED_PIN, HIGH);
    }
    else if (code == STOP)
    {
      target_current = 0;
      adjust_current(255, 4);
      do_tdcs = 0;
      set_potentiometer(255);
      digitalWrite(TDCS_LED_PIN, LOW);
    }
    else if (code == START_HARSH)
    {
      do_tdcs = 1;
      set_potentiometer(0);
      adjust_current(255, 0);
      digitalWrite(TDCS_LED_PIN, HIGH);
    }
    else if (code == STOP_HARSH)
    {
      do_tdcs = 0;
      set_potentiometer(255);
      digitalWrite(TDCS_LED_PIN, LOW);
    }
    else if (code == QUERY)
    {
      Serial.println(voltage, 5);
      Serial.println(current, 5);
      Serial.println(return_resistance, 5);
      Serial.println(potentiometer_resistance, 5);
    }
    else if (code >= SET_LOW && code <= SET_HIGH)
    {

      target_current = (double(code)-SET_LOW)/double((SET_HIGH-SET_LOW));
      target_current =5.0*target_current/1000.0;
      adjust_current(1, 0);
    }

  }
}

