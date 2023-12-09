//int tension = 0;
float starttime;
float endtime;
float starttime1;
float endtime1;
float starttime2;
float endtime2;

float t_prime = -1; 
float t_air = -1;   
float t_cycle = t_prime + t_air;

bool stringComplete1 = false; 
bool stringComplete2 = false;

String inputString;

void setup() {
  Serial.begin(9600);
  //delay(2000); 
  inputString.reserve(200); 

  pinMode(9, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);

  Serial.println("Aguardando dados pela porta serial...");
  //Serial.println("Aqui1");

  while (true) {
    while (Serial.available() > 0) {
      //Serial.println("Aqui2");
      char inChar = (char)Serial.read();
      Serial.println(inChar);
      inputString += inChar;

      if (inChar == ';') {
        if (!stringComplete1) {
          stringComplete1 = true;
        } else {
          stringComplete2 = true;
          break;  // Sai do loop assim que receber a segunda parte da string
        }
      }
    }

    if (stringComplete1 && stringComplete2) {
      int index1 = inputString.indexOf(';');
      int index2 = inputString.lastIndexOf(';');

      if (index1 != -1 && index2 != -1 && index1 < index2) {
        t_prime = inputString.substring(0, index1).toFloat();
        t_air = inputString.substring(index1 + 1, index2).toFloat();
        t_cycle = t_prime + t_air;
        Serial.println("Dados recebidos com sucesso!");
        Serial.println("t_prime: " + String(t_prime));
        Serial.println("t_air: " + String(t_air));
        Serial.println("t_cycle: " + String(t_cycle));
        
        
        inputString = "";
        stringComplete1 = false;
        stringComplete2 = false;
        //Serial.println("Aqui3");
        
        // Sai do loop de setup pra entrar no loop principal
        break;
      } else {
        Serial.println("Erro nos dados. Verifique o formato (tempo1;tempo2;).");
       
      }
    }

    delay(10); 
  }
}





void loop() {
    starttime = millis();
    endtime = starttime;
    while((endtime - starttime) <= (t_cycle*3000*0.997)) //pour les COVs
    {
    starttime1 = millis();
    endtime1 = starttime1;
    while((endtime1 - starttime1) <= t_prime*1000){
      digitalWrite(9, LOW);
      digitalWrite(11, HIGH);
      digitalWrite(12, HIGH);
      endtime1 = millis();
    }
    
    starttime2 = millis();
    endtime2 = starttime2;
    
    while ((endtime2 - starttime2) <= t_air*1000){
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
  while((endtime - starttime) <= (t_cycle*3000*0.997))   //pour l'azote
  {
    digitalWrite(11, LOW);                          
    digitalWrite(9, LOW); 
    digitalWrite(12, LOW);    
    endtime = millis();
    delay(250);
  }
  delay(250);
  Serial.println("Loop principal concluído. Aguardando novos dados pela porta serial...");
  while (true) {
    //Serial.println("Aqui3");
    delay(20); 
    //Serial.println("Aqui4");
    if (Serial.available() > 0) {
      Serial.println("Aqui5");
      setup();
      break;
    }
  }
}
