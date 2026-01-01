#!/usr/bin/env python3
import os
import sys
import csv
import sqlite3
import logging

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
        if name.split('.')[1] == 'csv': yield name

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
    
def procesar_file( data: dict, dir: str = '.', filename: str =''):
    '''
    Prossesa ficheros csv producidos por inventarios
    '''
    logging.info(f'prosesando el fichero: {filename}' )
    
    ruta_fichero = os.path.join(dir, filename)    
    medios = []
    
    # Procesando cabesera
    with open(ruta_fichero, newline='') as f:
        reader = csv.reader(f)
        linea = 1
        colum = 0
        for row in reader:
            colum = 0
            for campo in row:                
                if campo == '': 
                    colum += 1
                    continue
                if campo.strip().lower() == 'Empresa:'.lower() : 
                    #print(f'Fila: {linea}, Columna: {colum}')
                    #print(row)
                    data['Empresa'] = row[colum + 1].strip()
                    break
                if campo.strip().lower() == 'Centro de Costo:'.lower() : 
                    data['Centro'] = row[colum + 1].strip()
                    break
                if campo.strip().lower() == 'Area de Responsabilidad:'.lower() :
                    data['Area'] = row[colum+1].strip()
                    break
                if campo.strip().lower() == 'Tipo de Activo:'.lower() :
                    data['Tipo'] = row[colum+1].strip()
                    break
                if 'Utiles y Herramientas'.lower() in campo.strip().lower():
                    data['Tipo'] = 'Utiles y Herramientas'
                
                colum += 1
            
            linea += 1
            data['Linea']= linea
            if ('Area' in data) and ('Tipo' in data): 
                logging.info(f'Cabesera {data}')
                break
    
    # Procesando data tipo 'tangible'
    def get_data_tangible(Linea: int = 0):
        logging.debug(f'entrando en "get_data_tangible()"')
        with open(ruta_fichero, newline='') as f:
            reader = csv.reader(f)
            l = 0
            for row in reader:                
                if row[0] == '': continue

                if row[0].strip()[1].isnumeric() and l >= Linea:
                    logging.info(f'prosesando la fila {Linea + l}')
                    logging.info(f'--> {row}')
                    if '/' in row[0].strip(): continue
                    d ={'Codigo':row[0].strip(),
                           'Des':row[1].strip(),
                         'FAlta':row[8].strip(),
                         'FActu':row[9].strip()}
                    medios.append(d)
                    logging.info(f'Datos Resultado {d}')
                l +=1
    
    # Procesando datos tipos 'Utiles y Herramientas'
    def get_data_UtilHerami(Linea: int = 0):
        with open(ruta_fichero, newline='') as f:
            reader = csv.reader(f)
            l = 0
            fase = 0
            util ={}
            
            for row in reader:
                                
                if (fase == 3) and (l >= Linea):
                    if util['Codigo'] != '' :medios.append(util)                    
                    util = {}
                    #print(medios)                    
                    fase = 0
                    l +=1
                    continue
                
                if (fase == 2) and (l >= Linea):
                    util['Cantida'] = row[2].strip()
                    util['Precio'] = row[3].strip()
                    util['Importe'] = row[4].strip()                    
                    fase += 1
                    l +=1
                    continue
                
                if (fase == 1) and (l >= Linea):                    
                    #if '/' in row[0].strip(): continue
                    util['Codigo'] = row[0].strip()
                    util['Des'] = row[1].strip()
                    #print()                    
                    #print(f'Fase: {fase}, linea: {l}, IF: 1')
                    #print('-------------------------')
                    #print(row)
                    fase += 1
                    l +=1
                    continue
                
                if (fase == 0) and (l >= Linea): 
                    #print()                    
                    #print(f'Fase: {fase}, linea: {l}, IF: 0')
                    #print('-------------------------')
                    #print(row)
                    fase += 1
                    l +=1
                    continue
                
                l += 1
    
    if data['Tipo'] == '1 - Tangible':
        get_data_tangible(data['Linea'])
    
    if data['Tipo'] == 'Utiles y Herramientas':
        get_data_UtilHerami(data['Linea'])
        pass
    
    data['Medios']= medios
    print('...Archivo procesado...')
    return data

def savemedios(datos: dict = {}, filename: str = ''):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Codigo', 'Des', 'Area', 'FAlta', 'FActu']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for medio in datos['Medios']:
            medio['Area'] = datos['Area']
            #print(medio)
            writer.writerow(medio)
    
def saveutiles(datos: dict = {}, filename: str = ''):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Codigo', 'Des', 'Cantida', 'Area', 'Precio', 'Importe']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
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
    
    # interamos por cada fichero en el directorio    
    for filename in files_is_csv(wd):
        datos = {} # Almacen para los datos obtenidos        
        procesar_file(datos, wd, filename)
                
        # Guardondo los datos segun el tipo en ficheros apropiados
        if datos['Tipo'] == '1 - Tangible':
            savemedios(datos, filenamemedios)
    
        if datos['Tipo'] == 'Utiles y Herramientas':
            saveutiles(datos, filenameutiles)    
    
    #conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(f'Uso: {sys.argv[0]} [test]')
        sys.exit(0)
    if sys.argv[1] == 'test':
        logging.debug(f'Ejecutando pruebas')
        import doctest
        doctest.testmod() # ejecuta automáticamente las pruebas integradas
        sys.exit(0)
    main()