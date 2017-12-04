import sys
import pymongo 
from pymongo import MongoClient
from config import *

#Funcion que guarda el resultado de las peticiones en una base de datos Mongo

def conexion_db_mongo(x):
    client = MongoClient(URI)
    print('Conexion con Base de datos OK')
    db = client['logs_bd']
    col = db['logs_col']
    try:
        insertar_log = col.insert_one(x)
        if insertar_log.acknowledged == True:
            print('Petición actual: ', x)
            print ('Log guardado con exito')
    except:
        print('Error no contemplado:', sys.exc_info())