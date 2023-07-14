import sqlite3
import numpy as np
import os
import re
import pandas as pd



banco = sqlite3.connect('/home/hewerton/Documentos/WRL_BETA/database.db')
cursor = banco.cursor()

def criar_tabela_usinas():
    cursor.execute ("CREATE TABLE IF NOT EXISTS Usinas (id TEXT, REGIAO TEXT,País TEXT,Grupo TEXT,Site TEXT,BOF TEXT,Capacity TEXT,Lanças TEXT,Carros TEXT)")
    banco.commit()

def criar_tabela_dados():
    cursor.execute (f"CREATE TABLE IF NOT EXISTS Dados (REGIAO TEXT,País TEXT,Grupo TEXT,Site TEXT,BOF TEXT,Capacity TEXT,Lanças TEXT,Carros TEXT\
    ,Bico_id TEXT,Tipo TEXT, Vida TEXT,Posição TEXT, Carro TEXT, Convertedor TEXT, Operador TEXT, Data Text,Angulo Text,D1 TEXT,D2 TEXT,D3 TEXT,D4 TEXT,D5 TEXT,D6 TEXT,D_Externo TEXT)")
    banco.commit()

def insert_usina(id,regiao,pais,grupo,site,bof,capacity,lancas,carros):
    cursor.execute (f"INSERT INTO Usinas VALUES ('{id}','{regiao}','{pais}','{grupo}','{site}','{bof}','{capacity}','{lancas}','{carros}')")
    banco.commit()

def insert_dados(regiao,pais,grupo,site,bof,capacity,lancas,carros,bico_id,tipo,posicao,carro,convertedor):
    cursor.execute (f"INSERT INTO Dados (REGIAO,País,Grupo,Site,BOF,Lanças,Capacity,Carros,Bico_id,Tipo,Posição,Carro,Convertedor) VALUES ('{regiao}','{pais}','{grupo}',\
    '{site}','{bof}','{lancas}','{capacity}','{carros}','{bico_id}','{tipo}','{posicao}','{carro}','{convertedor}')")
    banco.commit()

def insert_dados_inspec(regiao,pais,grupo,site,bof,capacity,lancas,carros,bico_id,tipo,posicao,carro,vida,operador,data,Convertedor):
    cursor.execute (f"INSERT INTO Dados (REGIAO,País,Grupo,Site,BOF,Lanças,Capacity,Carros,Bico_id,Tipo,Posição,Carro,Vida,Operador,Data,Convertedor) VALUES ('{regiao}','{pais}','{grupo}',\
    '{site}','{bof}','{lancas}','{capacity}','{carros}','{bico_id}','{tipo}','{posicao}','{carro}','{vida}','{operador}','{data}','{Convertedor}')")
    banco.commit()

def insert_dados_bico(nome_usina,codigo,tipo,convertedor,carro):
    cursor.execute (f"INSERT INTO dados (id,Tipo,Usina,Convertedor,Carro) VALUES ('{codigo}','{tipo}','{nome_usina}','{convertedor}','{carro}')")
    banco.commit()

def delete_dados(nome_tabela,col1,cond1,col2,cond2,*args,mode=False):
    comando = f"DELETE FROM {nome_tabela} WHERE {col1}='{cond1}' AND {col2}='{cond2}'"
    if mode == False:
        comando = f"DELETE FROM {nome_tabela} WHERE {col1}='{cond1}' AND {col2}='{cond2}'"
    elif mode == True:
         comando = f"DELETE FROM {nome_tabela} WHERE {col1}='{cond1}' AND {col2}='{cond2}' AND Vida IS NULL"
         
    for i in range(0,len(args),2):
        comando = comando+f" AND {args[i]}='{args[i+1]}'"

    print(comando) 
    cursor.execute(comando)
    banco.commit()

def atualizar(tabela_nome,coluna_nome, novo_dado, id):
    cursor.execute(f"UPDATE {tabela_nome} SET {coluna_nome} = '{novo_dado}' WHERE id = '{id}'")
    banco.commit()

def atualizar2(nome_tabela, coluna_nome, novo_dado, id,vida,site,pais):
    cursor.execute(f"UPDATE {nome_tabela} SET {coluna_nome} = '{novo_dado}' WHERE Bico_id = '{id}'\
        AND Vida = '{vida}'AND Site = '{site}'AND País = '{pais}';")
    banco.commit()

def atualizar3(tabela_nome,coluna_nome, novo_dado, vida):
    cursor.execute(f"UPDATE {tabela_nome} SET {coluna_nome} = '{novo_dado}' WHERE Vida = '{vida}'")
    banco.commit()

def update(nome_tabela,nome_coluna,novo_dado,cond,dado_existente,cond2,dado_existente2):
    cursor.execute(f"UPDATE {nome_tabela} SET {nome_coluna} = '{novo_dado}' WHERE {cond} = '{dado_existente}' AND {cond2} = '{dado_existente2}'")
    banco.commit()   

def preencher_diametro(nome_tabela,id,vida,site,pais, D1,D2,D3,D4,D5,D6,D_Externo,angulo):
    atualizar2(nome_tabela,'D1',D1,id,vida,site,pais)
    atualizar2(nome_tabela,'D2',D2,id,vida,site,pais)
    atualizar2(nome_tabela,'D3',D3,id,vida,site,pais)
    atualizar2(nome_tabela,'D4',D4,id,vida,site,pais)
    atualizar2(nome_tabela,'D5',D5,id,vida,site,pais)
    atualizar2(nome_tabela,'D6',D6,id,vida,site,pais)
    atualizar2(nome_tabela,'D_Externo',D_Externo,id,vida,site,pais)
    atualizar2(nome_tabela,'Angulo',angulo,id,vida,site,pais)

def dados_coluna(coluna):
    cursor.execute(f'SELECT {coluna} FROM Usinas')
    dados = []
    for coluna in cursor.fetchall():
        coluna = str(coluna)
        coluna = re.sub("\'|\)|\(|\,|\[","",coluna)
        dados.append(coluna)
    return dados

def check_table():
    a = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'AND name='Usinas'").fetchall()
    return a

def selecionar_linhas(coluna_nome,nome_tabela,cond,dado,nome_usina,dado2,pais,dado3):
    cursor.execute(f"SELECT {coluna_nome} FROM {nome_tabela} WHERE {cond} = '{dado}' AND {nome_usina} = '{dado2}' AND {pais} = '{dado3}'")
    row = cursor.fetchall()
    row = str(row)
    row = re.sub("\'|\)|\(|\,|\[|\]","",row)
    return row

def contar_linhas(nome_usina):
    cursor.execute('SELECT COUNT(*) FROM {}'.format(nome_usina))
    return cursor.fetchall()[0][0]

def extrair_dados(nome_usina):
    cursor.execute(f'SELECT * FROM {nome_usina}' )
    return cursor.fetchall()

def filtro(nome_tabela,regiao,pais,grupo,site):
    cursor.execute(f'SELECT * FROM {nome_tabela} WHERE REGIAO = "{regiao}" AND País = "{pais}"\
    AND Grupo = "{grupo}" AND Site = "{site}"' )
    return cursor.fetchall()

def ler_colunas(nome_coluna,nome_tabela,cond1,x,cond2,y):
   return cursor.execute(f'SELECT {nome_coluna} FROM {nome_tabela} WHERE {cond1} = "{x}" AND {cond2} = "{y}"').fetchall()
   
def ler_colunas2(nome_coluna,nome_tabela,cond1,x,cond2,y,cond3,z):
   return cursor.execute(f'SELECT {nome_coluna} FROM {nome_tabela} WHERE {cond1} = "{x}" AND {cond2} = "{y}" AND {cond3} = "{z}"').fetchall()

#def verifica_existencia(tabela_nome,coluna_nome1, dado1,coluna_nome2, dado2,coluna_nome3, dado3,coluna_nome4, dado4,coluna_nome5, dado5):
#    return cursor.execute(f"SELECT EXISTS(SELECT * FROM {tabela_nome} WHERE {coluna_nome1} = '{dado1}' AND {coluna_nome2} = '{dado2}'\
#        AND {coluna_nome3} = '{dado3}' AND {coluna_nome4} = '{dado4}' AND {coluna_nome5} = '{dado5}')").fetchone()[0]
        
def verifica_existencia(tabela_nome,coluna_nome,dado,**kwargs):
    comando = f"SELECT EXISTS(SELECT * FROM {tabela_nome} WHERE {coluna_nome} = '{dado}'"
    for key,value in kwargs.items():
        comando = comando +f" AND {key}='{value}'"
    comando += ')'
    return cursor.execute(comando).fetchone()[0]


def check_values(nome_tabela,coluna_nome1, dado1,coluna_nome2, dado2,coluna_nome3, dado3,coluna_nome4, dado4):
     return cursor.execute(f"SELECT EXISTS(SELECT * FROM {nome_tabela} WHERE {coluna_nome1} = '{dado1}' AND\
         {coluna_nome2} = '{dado2}' AND {coluna_nome3} = '{dado3}' AND {coluna_nome4} = '{dado4}')").fetchone()[0]


def check_null(nome_tabela,coluna_nome1,coluna_nome2, dado2,coluna_nome3, dado3,coluna_nome4, dado4,*args):
    comando = f"SELECT EXISTS(SELECT * FROM {nome_tabela} WHERE {coluna_nome1} IS NULL AND {coluna_nome2} = '{dado2}'\
        AND {coluna_nome3} = '{dado3}' AND {coluna_nome4} = '{dado4}'"
    
    for i in range(0,len(args),2):
        comando = comando+f" AND {args[i]}='{args[i+1]}'"
    comando= comando+")"
    return cursor.execute(comando).fetchone()[0]

def verifica_espacos(string):
    if " " in string:
            string = string.replace(" ","_")
    else:
        pass
    return string

def acessar_dado_pontual(dado_requerido,tabela_nome,coluna_nome,dado):
    return cursor.execute(f"SELECT {dado_requerido} FROM {tabela_nome} WHERE {coluna_nome} = '{dado}'").fetchall()

def acessa_dado_4_cond(dado_requerido,tabela_nome,coluna_nome,dado,coluna_nome2,dado2,coluna_nome3,dado3,coluna_nome4,dado4):
    return cursor.execute(f"SELECT {dado_requerido} FROM {tabela_nome} WHERE {coluna_nome} = '{dado}' AND {coluna_nome2} = '{dado2}'\
        AND {coluna_nome3} = '{dado3}'AND {coluna_nome4} = '{dado4}'").fetchall()

def acessar_dados(dado_requerido,tabela_nome,coluna_nome,dado,**kwargs):
	comando=f"SELECT {dado_requerido} FROM {tabela_nome} WHERE {coluna_nome} = '{dado}'"
	for key,value in kwargs.items():
		comando = comando +f" AND {key} = '{value}'"
	return cursor.execute(comando).fetchall()

def check_caixa_vazia(a):
    if a == '' or a.isspace():
        return True
    else:
        return False

if __name__ == "__main__":
    #print('aaaaa',str(os.path.dirname(os.path.abspath(__file__))))
    print(acessa_dado_4_cond('Tipo','dados','Grupo','Usiminas','Site','Ipatinga1','bico_id','1','bico_id','1')[0][0])
