#!/usr/bin/env python3
import os
import sys
import csv
import sqlite3
import logging
import argparse

def ListAreas(conexion):
    '''
    Lista las areas existentes en la db
    '''
    cursor = conexion.cursor()
    query = "SELECT * FROM inventarios_area"
    areas = cursor.execute(query).fetchall()
    for area in areas:
        print(area)

def AddArea(conexion, codigo, descripcion):
    '''
    Agrega areas a la db
    '''
    cursor=conexion.cursor()
    try:
        cursor.execute("INSERT INTO inventarios_area (Codigo, Descriccion) VALUES (?,?)",
               (codigo, descripcion))
        conn.commit()
    except sqlite3.IntegrityError:
        # Ya existe esta area
        pass        

def files_in_dir(dir: str = '.'):
    '''
    itera en las entradas de directorios y devuelve nombres de las que sean ficheros.
    '''
    for direntry in os.scandir(dir):
            #print(direntry.name, end='')
            if direntry.is_file(): yield direntry.name #print(' Fichero')
            pass

def files_is_csv(dir: str = '.'):
    '''
    itera en la entrada y devuelve los ficheros csv
    '''
    for name in files_in_dir(dir):
        if name.split('.')[-1] == 'csv': yield name

def print_dic(dic: dict):
    '''
    Imprime un dicionario
    '''
    for k, v in dic.items():
            if k == 'Medios':                
                for item in v:
                    print(item)
            else:
                print(k, ' -> ', v)
    
def keys_in_dict(dic: dict = {}, list: list =[]) -> bool:
    '''
    Evalúa si en dic están presente todas las claves pasadas en list
    
    >>> keys_in_dict({'key1':4, 'key2'= 'valor'},['key1', 'key2'])
    True
    
    >>> keys_in_dict({'key1':4, 'key2'= 'valor'},['key1', 'key3'])
    False
    '''
    
    #logging.debug(f'src69 Dentro de keys_in_dict')
    #logging.debug(f'Claves en diccionario {dic.keys()}')
    #logging.debug(f'Claves pasadas {list}')
    for elemento in list:
        if not (elemento in dic): 
            #logging.debug(f'Retornando False')
            return False
    
    #logging.debug(f'Retornando True')
    return True
        
def procesar_file( data: dict, dir: str = '.', filename: str =''):
    '''
    Procesa ficheros csv producidos por inventarios
    '''
    logging.info(f'Procesando el fichero: {filename}' )
    
    ruta_fichero = os.path.join(dir, filename)    
    medios = []
    
    claves_verificar = ['Empresa', 'Centro', 'Area', 'Tipo']
    
    linea = 1
    columna = 0
    fase = 0
    util ={}
    
    # Procesando el fichero    
    with open(ruta_fichero, newline='') as f:
        reader = csv.reader(f)    
        
        # por cada linea
        for row in reader:
            logging.info(f'Procesando la linea {linea}')
            logging.info(f'--> {row}')
            
            # Procesando cabecera
            if not keys_in_dict(data, claves_verificar):
                #logging.info(f'Procesando cabecera')
                columna = 0
                for campo in row:
                    #logging.info(f'Procesando linea: {linea}, columna: {columna}')
                    if campo == '': 
                        #logging.info(f'Campo vació, pasamos al siguiente')
                        columna += 1
                        continue
                    if campo.strip().lower() == 'Empresa:'.lower() :
                        #logging.info(f'Se encontró e campo "Empresa"')
                        data['Empresa'] = row[columna + 1].strip()
                        break
                    if campo.strip().lower() == 'Centro de Costo:'.lower() :
                        #logging.info(f'Se encontro el campo "Centro de Costo"')
                        data['Centro'] = row[columna + 1].strip()
                        break
                    if campo.strip().lower() == 'Area de Responsabilidad:'.lower() :
                        #logging.info(f'Se encontro el campo "Area"')
                        data['Area'] = row[columna+1].strip()
                        break
                    if campo.strip().lower() == 'Tipo de Activo:'.lower() :
                        #logging.info(f'Se encontró el campo "Tipo" para Activos')
                        data['Tipo'] = row[columna+1].strip()
                        break
                    if 'Utiles'.lower() in campo.strip().lower():
                        #logging.info(f'Se encontró el campo "Tipo" para Útiles')
                        data['Tipo'] = 'Utiles'
                        break
                                            
                    columna += 1
                
            #if keys_in_dict(data, claves_verificar):
            else:
                logging.info(f'Cabecera completa, empezamos con el cuerpo')
                # Procesando data tipo 'tangible'
                if data['Tipo'] == '1 - Tangible':            
                    logging.debug(f'Procesando data tipo "Activos"')
                    if row[0] == '':
                        logging.info(f'Linea vacía, pasamos a la siguiente')
                        linea += 1
                        continue
                    if row[0].strip()[1].isnumeric() :                        
                        if '/' in row[0].strip(): continue
                        d ={'Codigo':row[0].strip(),
                               'Des':row[1].strip(),
                             'FAlta':row[8].strip(),
                             'FActu':row[9].strip()}
                        medios.append(d)
                        logging.info(f'Datos Resultado {d}')

                # Procesando datos tipos 'Utiles'
                if data['Tipo'] == 'Utiles':
                    logging.debug(f'Procesando data tipo "Útiles", linea {linea}' )
                    if (fase == 3) and (linea >=13):
                        logging.info(f'Face: {fase}, guardamos y pasamos el siguiente')
                        if util['Codigo'] != '' :medios.append(util)                    
                        util = {}
                        #print(medios)                    
                        fase = 0
                        linea += 1
                        continue
                    
                    if (fase == 2) and (linea >=13):
                        logging.info(f'Face: {fase}, obtenemos el resto de la info')
                        util['Cantida'] = row[2].strip()
                        util['Precio'] = row[3].strip()
                        util['Importe'] = row[4].strip()                    
                        fase += 1
                        linea += 1
                        continue
                    
                    if (fase == 1) and (linea >=13):
                        logging.info(f'Face: {fase}, Contiene código y descripción')
                        util['Codigo'] = row[0].strip()
                        util['Des'] = row[1].strip()                    
                        fase += 1
                        linea += 1
                        continue
                    
                    if (fase == 0) and (linea >=13):
                        logging.info(f'Face: {fase}, linea se supone vacía')
                        fase += 1
                        linea += 1
                        continue
            
            linea += 1
            data['Linea']= linea
    
    logging.info(f'Terminamos en fichero -----')
    data['Medios']= medios    
    return data

def savemedios(datos: dict = {}, filename: str = ''):
    isnuevofile = not os.path.exists(filename)
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Codigo', 'Des', 'Area', 'FAlta', 'FActu']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if isnuevofile : writer.writeheader()
        
        for medio in datos['Medios']:
            medio['Area'] = datos['Area']
            #print(medio)
            writer.writerow(medio)
    
def saveutiles(datos: dict = {}, filename: str = ''):
    isnuevofile = not os.path.exists(filename)
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Codigo', 'Des', 'Cantida', 'Area', 'Precio', 'Importe']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if isnuevofile : writer.writeheader()
        
        for medio in datos['Medios']:
            medio['Area'] = datos['Area']
            #print(medio)
            writer.writerow(medio)

def main():
    # Configuración básica para log en archivo
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', mode='a')  # append, un mensaje por línea
        ]
    )
    #logging.debug('Mensaje de depuración')
    #logging.info('Mensaje de información')
    #logging.warning('Mensaje de advertencia')
    #logging.error('Mensaje de error')
    #logging.critical('Mensaje crítico')
    
    wd=os.getcwd()
    logging.info(f'Trabajando en el directorio {wd}')
    
    # preparar el directorio para los resultados
    dirresultados=os.path.join(wd, 'resultado')    
    try:
        os.mkdir(dirresultados)
        logging.info(f'Los resultados se guardan en {dirresultados}')
    except FileExistsError:
        logging.info(f'Los resultados se guardan en {dirresultados} que ya existe')
    
    # Coneccion a la base de datos, en su momento 
    #conn = sqlite3.connect('db.sqlite3')
    
    # ficheros para los resultados
    filenameutiles = os.path.join(dirresultados, 'Utiles.csv')
    filenamemedios = os.path.join(dirresultados, 'Medios.csv')
    
    #ListAreas(conn)
    #AddArea(conn,'200312','Dpto. de Derecho')
    
    # iteramos por cada fichero en el directorio    
    for filename in files_is_csv(wd):
        datos = {} # Almacen para los datos obtenidos        
        procesar_file(datos, wd, filename)
                
        # Guardondo los datos segun el tipo en ficheros apropiados
        if datos['Tipo'] == '1 - Tangible':
            savemedios(datos, filenamemedios)
    
        if datos['Tipo'] == 'Utiles':
            saveutiles(datos, filenameutiles)    
    
    #conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="increase output-test")
    args = parser.parse_args()
    if args.test:
        print('-test turned on')    
        logging.debug(f'Ejecutando pruebas')
        import doctest
        doctest.testmod() # ejecuta automáticamente las pruebas integradas
        sys.exit(0)
    main()