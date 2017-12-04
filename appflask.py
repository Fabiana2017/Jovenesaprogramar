from flask import Flask, request, make_response, render_template, Response
from functools import wraps
from plani import *
from sentiment import *
import datetime
import pymongo 
from pymongo import MongoClient
import sys
import json

# Control Autenticacion

def control_autent(username, password):

    ''' http://flask.pocoo.org/snippets/8/ Esta función es llamada 
    para verificar si una combinacion de usuario y password es válida'''

    users_ = json.load(open('config.json'))['usuarios']
    for u in users_:
        if u['username'] == username and u['password'] == password: 
            return True
    return False

def autenticacion():
    # Envía respuesta 401 (Código de estado HTTP del lado cliente: "Unauthorized")
    return Response(
    'Datos de acceso no válidos', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def autent_requerida(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not control_autent(auth.username, auth.password):
            return autenticacion()
        return f(*args, **kwargs)
    return decorated

# Roles

def roles_(f):
    @wraps(f)
    def rolesconf(*args, **kwargs):
        usuario_ = request.authorization['username']
        servicio_ = request.url_rule
        
        with open("config.json", encoding="UTF-8") as a:
            config_ = json.load(a)
            dato_usuario = config_["usuarios"]
            dato_rol = config_["roles"]
        
        rol_ = ''
        for y in range(len(dato_usuario)):
            if usuario_ == dato_usuario[y]["nombre"]:
                rol_ = dato_usuario[y]["rol"]
                break   
        if str(servicio_) in dato_rol[rol_]["servicios"]:
            return f(*args, **kwargs)
        else:
            return Response(("Unathorized"), 401)
    return rolesconf

# Porcentaje (aggregation)

def porcentaje(datos_p, cantid_t):
    datos_por = {}
    for x in datos_p:
        # Regla de tres
        datos_por[x] = [x] *100 /cantid_t

# Cantidad (aggregation)

def cantidad(plani_, cabezal_):
    cant_ = {}
    total_ = 0
    for z in range(1, len(plani_ -1)):
        valor = str(plani_[z][cabezal_])
        if valor in cant_.keys():
            cant_[valor] += 1
            total_ += 1
        else:
            cant_[valor] = 1
            total_ = 1
    r = {"cantidad": cant_, "porcentaje": porcentaje(cant_, total_)}
    return r

# Inicialización de la app Flask

app = Flask(__name__)

'''
Funcion after_request que captura las peticiones resueltas y devuelve valores de interes
para crear un log y guardarlo en Mongo DB
'''

'''
Modificación de logs.
- Si está autenticado: usuario que hizo la consulta
- Dirección IP y puerto del que hizo la consulta
- Servicio invocado
'''

@app.after_request
def peticion_resuelta(response):
        log_ =   {
    
    'fecha_invocacion': str(datetime.now()),
    'estado': {
        'codigo': response.status_code,
        'texto': response.status
            },
    'respuesta': {
        'largo': response.content_length,
        'tipo': response.content_type,
        'mimetype': response.mimetype}
    'usuario':{
        'nickname': request.authorization['username']
        'ip_usuario': request.environ['REMOTE_ADDR'],
        'puerto_usuario': request.environ['REMOTE_PORT'],
        'servicio': str(request.url_rule)

            }
    }
        logs_mongo.conexion_db_mongo(log_)
        return response

# Endpoint microdatos con autenticacion, que devuelve todos los resultados de la planilla en un archivo csv

@app.route('/microdatos')
@autent_requerida
@roles_
def microdatos():
    # Compruebo que request.args reciba parámetros y abro el archivo de config
    if len(request.args) > 0:
        with open("config.json", encoding="UTF-8") as a:
            filtros_ = json.load(a)["config_servicio"]["filters"]
            param_ = request.args # Variable que guarda los parametros que recibe

            for i in param_:
                if i not in filtros_:
                    #Si se equivoca, mensaje de error 400
                    return (Response('400 Bad Request: Error en los parámetros', 400))
                else:
                    return plani.main()
    else:
        return (Response('400 Bad Request: Parámetros sin especificar', 400))

# Agregar servicio (ruta) de resultados (datos agregados) que devuelva los resultados en formato JSON.

@app.route('/resultados_')
@autent_requerida
@roles_
def results():

    # Invoco función que devuelve los datos de la planilla, función que devuelve cantidad, y función que analiza lenguaje natural
    # Recordar que los parámetros de la funcion cantidad, son: planilla y cabezal

    valor_ = plani.devolver_valores()
    resultado = { 'aggregation': {'Edad': cantidad(valor_, 2),

                                        'Género': cantidad(valor_, 3)},
                    {'sentiment': {'Si conoce del programa "Jóvenes a programar", ¿qué opinión tiene acerca del mismo?': analizar_sentimiento(valor_)}
                }
            }

    return (json.dumps(resultado))

@app.route('/')
def index():
    return render_template('index.html').format(username=request.authorization['username'])

if __name__ == '__main__':
        app.run()




