
/* MC853 1s2019 - Projeto Final: Sensor de Batimento Cardiaco
   Professor Celio Cardoso Guimaraes
   Autores :
      Raphael Pontes Santana - Ra176414
      Vitor Kenji Uema       - Ra157465 */

#define USE_ARDUINO_INTERRUPTS false
#include <PulseSensorPlayground.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

extern "C"{
#include "user_interface.h"
}

PulseSensorPlayground pulseSensor;
WiFiClient WiFiClient;
PubSubClient client(WiFiClient);

#define ssid "aula-ic3"
#define password "iotic@2019"

// servidor mqtt, porta nao cifrada
#define SERVER "xaveco.lab.ic.unicamp.br"
#define SERVERPORT 1883

// topicos
// ultima parte de topico eh o nome do usuario
#define TOPIC1 "sensor/pulsesensor/signal/vitor"
#define TOPIC2 "sensor/pulsesensor/bpm/vitor"
#define TOPIC3 "sensor/pulsesensor/ibi/vitor"

// ID do usuario
#define userID "vitor"

// sensor conectado no pino A0
#define PULSE_INPUT 0
// on-board Arduion LED
#define LED13 D0

// a partir de qual valor eh considerado uma batida
#define Threshold 700

void setup() {
  // led pisca deacodordo com a frequencia cardiaca
  pinMode(LED13,OUTPUT);
  Serial.begin(9600);

  //Configuracao do Sensor de Pulso
  pulseSensor.analogInput(PULSE_INPUT);
  pulseSensor.setSerial(Serial);
  pulseSensor.setThreshold(Threshold);

  if (!pulseSensor.begin()){
    Serial.print("Nao foi possivel inicializar o sensor. Por favor verifique as configurações!");
    delay(50);
  }

  // conectar ao wi-fi
  delay(10);
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: "); 
  Serial.println(WiFi.localIP());
  WiFi.printDiag(Serial);
  client.setServer(SERVER, SERVERPORT);
}

/* funcao principal:
 * 1. conectar ao servidor mqtt
 * 2. ler o sinal do sensor
 * 3. caso o sinal for maior que o Threshold, marcar uma batida (borda de subida)
 * 4. BPM eh calculado com base na diferenca entre duas batidas
 * 5. enviar os dados coletados para o broker */
void loop() {
  int count = 0, batida = 0, counttosend = 0;
  int IBI;
  int BPM;
  int Signal;
  String resposta;
  char respostaChar[10];
  
  if (!client.connected()) { 
      Serial.println("Attempting MQTT connection...");

      if (client.connect(userID)) { 
        while (true) {
          if (pulseSensor.sawNewSample()){
          count++;

          Signal = pulseSensor.getLatestSample();
          if(Signal >= Threshold && !batida){
            digitalWrite(LED13,HIGH);
            BPM = 60000/(count*10);
            batida = 1;
            count = 0;
          }
            
          if(Signal < Threshold) {
            batida = 0;
            digitalWrite(LED13,LOW);
          }
            
          if(BPM > 250)
            BPM = 250;
            
          Serial.println(Signal);
          
          IBI = pulseSensor.getInterBeatIntervalMs();

          // enviar um pacote a cada 10 medicoes
          if( ++counttosend == 10){
            counttosend = 0;

            resposta = Signal;
            resposta.toCharArray(respostaChar, 10);
            client.publish(TOPIC1, respostaChar, true);

            resposta= BPM;
            resposta.toCharArray(respostaChar, 10);
            client.publish(TOPIC2, respostaChar, true);

            resposta = IBI;
            resposta.toCharArray(respostaChar, 10);
            client.publish(TOPIC3, respostaChar, true);

          }
          delay(10);
          client.loop();
          }
        } 
      }
      else {
        // nao foi possivel se conectar ao servidor
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.println(" try again in 4 seconds");
        // Wait 4 seconds before retrying
        delay(4000);
      }
  } 
}
  

