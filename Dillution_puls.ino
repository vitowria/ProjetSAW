int tension = 0;
float starttime;
float endtime;
float starttime1;
float endtime1;
float starttime2;
float endtime2;

float concentration_initial = -1; //related to the concentration 
float concentration_final = -1; //related to the concentration

int stringFlag = -1;

bool stringComplete1 = false; 
bool stringComplete2 = false;
//serialEvent 
//Começar com valor impossivel var1 var2
//setup colocar while alguma das duas com vlaor impossivel

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  inputString.reserve(200);

  pinMode(9, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);

  while (concentration_initial = -1 || concentration_initial = -1){
    if(stringComplete1 == true && stringComplete2 == true){
     concentration_initial = inputString.toFloat(inputString.substring(0, inputString.indexOf(';')));
     concentration_final = inputString.toFloat(inputString.substring(inputString.indexOf(';')+1, inputString.lastIndexOf(';')));
    }
    else{}
  }
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == ';' && stringComplete1=true) {
      stringComplete2 = true;
    }
    elsif (inChar == ';'){
      stringComplete1 = true;
    }
  }
}


void loop() {
  //variavel1 = 180000;
  //variavel2 = 180000;

  starttime = millis();
  endtime = starttime;
  while((endtime - starttime) <= (concentration_initial*0.997)) //pour les COVs
  {
    starttime1 = millis();
    endtime1 = starttime1;
    while((endtime1 - starttime1) <= 1000)
    {
      digitalWrite(9, LOW);
      digitalWrite(11, HIGH);
      digitalWrite(12, HIGH);
      endtime1 = millis();
    }
    
    starttime2 = millis();
    endtime2 = starttime2;
    while ((endtime2 - starttime2) <= 1000)
    {
      digitalWrite(11, LOW);
      digitalWrite(9, HIGH);
      digitalWrite(12, LOW);
      endtime2 = millis();
    }
    
    endtime = millis();
    delay(250);
  }
  starttime = millis();
  endtime = starttime;
  while((endtime - starttime) <= (concentration_final*0.997))   //pour l'azote
  {
    digitalWrite(11, LOW);                          
    digitalWrite(9, LOW); 
    digitalWrite(12, LOW);    
    endtime = millis();
    delay(250);
  }
  
  delay(250);
}
