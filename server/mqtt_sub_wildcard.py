# mc853 1s2019 - Projeto Final: Sensor de Batimento Cardiaco
# Professor Celio Cardoso Guimaraes
# Autores :
#   Raphael Pontes Santana - Ra176414
#   Vitor Kenji Uema       - Ra157465

from time import gmtime, strftime
import paho.mqtt.client as mqtt
import sqlite3

# certificado mqtt
certificado = "mosquitto-lab.crt"

# servidor xaveco
xaveco = "xaveco.lab.ic.unicamp.br"

# topico para receber dados de difersas pessoas
topic = "sensor/pulsesensor/signal/#"

# nome do arquivo do banco de dados
dbFile = "Health.db"

# variaveis globais
db = None
c = None
signalPoints = '['
count = 0

# conectar ao banco de dados
def connectDB(DBname):
    global db, c
    db = sqlite3.connect(dbFile)
    c = db.cursor()

# criar nova tabela
# cada linha possui dois campos:
# 1. <text> horario de recebiemento da mensagem (chave primaria)
# 2. <text> conteudo da mensagem
def createTable(tableName):
    global db, c
    c.execute('CREATE TABLE {}'.format(tableName) +
             '''(dataHorario text primary key, heartBeatWave text)''')
    db.commit()

# escrever nova linha na tabela
def writeOnDB(tableName, dataHorario, message):
    global db, c
    c.execute('INSERT INTO {}'.format(tableName) + '''
                VALUES (?, ?)''', (dataHorario, message))
    db.commit()

# escrever mensagen recebida no banco de dados
# se ja exitir tabela (usuario antigo), escrever mensagem no bando de dados
# caso contrario (novo usuario), criar nova tabela e escrever mensagem
def writeMessage(new_user, time, message):
    global db, c

    connectDB(dbFile)

    try:
        writeOnDB(new_user, time, message)
    except:
        createTable(new_user)
        writeOnDB(new_user, time, message)

    db.close()

# processamento da mensagem recebida
# escrever no bando de dados, quando receber 100 pontos
# da curva do eletrocardiograma.
def on_message(client,userdata,message):
    global signalPoints, count
    count = count + 1
    # nome do usuario eh o ultimo campo do topico
    new_user = message.topic.split('/')[-1]

    data = message.payload

    print (data)

    # colocar cada novo ponto da curva numa lista
    if (signalPoints == '['):
        signalPoints = signalPoints + data
    else:
        signalPoints =  signalPoints + ' ,'  + data

    if(count == 100):
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print time
        signalPoints = signalPoints + ']'
        writeMessage(new_user, time, signalPoints)
        print(signalPoints)
        signalPoints = '['
        count = 0

def make_mqtt_client():
    # conexao com o servidor mqtt da xaveco
    client = mqtt.Client()
    client.tls_set(certificado)

    client.on_message = on_message
    res = client.connect(xaveco, 8883, 10)

    print ("connection result = ", res)

    client.subscribe(topic)

    client.loop_forever()

if __name__ == '__main__':
    make_mqtt_client()
