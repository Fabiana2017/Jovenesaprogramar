from plani import *
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.NaturalLanguageUnderstandingV1 import Features, SentimentOptions

def analizar_sentimiento(p):

	# Guardo en una variable las credenciales de la api Natural Language Understanding

	cred_watson_ = json.load(open('config.json'))["cred_watson"]
	analizar_lenguajenatural = NaturalLanguageUnderstandingV1(version=cred_watson_["version"], 
		username=cred_watson_["username"], password=cred_watson_["password"])

	# Creo una variable que guarde un diccionario con valores inicciales de positivo, neutro y negativo

	valores_sentiment = {"positivo": 0, "neutro": 0, "negativo": 0}

	# Recorro planilla

	for r in range(1, len(p-1)):
		texto_ = p[r][14] # Si conoce del programa "Jóvenes a programar", ¿qué opinión tiene acerca del mismo?
		if (len(texto) > 10):
			analize_ = analizar_lenguajenatural.analize(text=texto_, features=Features(sentiment=SentimentOptions()))
			sentiment_ = analize_["sentiment"]["document"]["label"]
			if (sentiment_ == "positive"):
				# Si se cumple la condición, agrego valores al diccionario
				valores_sentiment["positivo"] += 1
			elif (sentiment_ == "neutral"):
				valores_sentiment["neutro"] += 1
			else:
				valores_sentiment["negativo"] += 1
	return valores_sentiment

