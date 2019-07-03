# mc853 1s2019 - Projeto Final: Sensor de Batimento Cardiaco
# Professor Celio Cardoso Guimaraes
# Autores :
#   Raphael Pontes Santana - Ra176414
#   Vitor Kenji Uema       - Ra157465

import sys
import sqlite3
import itertools
import matplotlib.pyplot as plt
import pandas as pd

# nome do arquivo do banco de dados
dbFile = "Health.db"

# gerar o grafico do eletrocardiograma
def graph(nome):

    # conectar ao banco de dados e
    # listar os valores como sendo uma lista e nao uma tupla
    db = sqlite3.connect(dbFile)
    db.row_factory = lambda cursor, row: row[0]
    c = db.cursor()

    # carregar todos os valores
    wavePoints = c.execute('SELECT heartBeatWave FROM {} DESC LIMIT 1'.format(nome)).fetchall()

    # converter unicode para ascii
    wavePoints = list(map(lambda l: l.encode('ascii','ignore'), wavePoints))
    # converter string para list
    wavePoints = list(map(lambda l: eval(l), wavePoints))
    # converter lista de listas para lista
    wavePoints = sum(wavePoints, [])

    # gerar o index de cada ponto da curva
    index = [i for i in range(len(wavePoints))]

    # gerar o grafico
    plt.plot(index, wavePoints)
    plt.show()

    # fechar o banco de dados
    db.close()

# imprimir tabela
def table(nome):
    db = sqlite3.connect(dbFile)
    print pd.read_sql_query('SELECT heartBeatWave FROM {}'.format(nome), db)

# deletar tabela
def delete(nome):
    db = sqlite3.connect(dbFile)
    c = db.cursor()

    c.execute('DROP TABLE {}'.format(nome))

# primeiro argumeto: nome da operacao (graph, table ou delete)
# segundo arguemento: nome da pessoa
def main():
    try:
        op = eval(sys.argv[1])
        try:
            op(sys.argv[2])
        except:
            print('perfil nao encontrado')
    except:
        print('verifique nome da operacao')

if __name__ == '__main__':
    main()
