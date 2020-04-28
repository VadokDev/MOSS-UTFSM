
import pandas as pd
from operator import methodcaller as mc

class AlumnosReader:
	"""Módulo de Python encargado de extraer la información del archivo de alumnos de cada paralelo"""

	START_INDEX_PARALELO = 8
	
	"""
	loadFile - Carga los datos de la 1era página de un archivo .xlsx en memoria desde la fila start.

	:string fileName: directorio/nombre del archivo
	:int start: fila desde donde cargar los datos (comienza de 0)
	:returns: lista con los datos del excel desde la fila start 
	"""
	def loadFile(fileName, start):
		xl = pd.ExcelFile(fileName)
		return xl.parse(xl.sheet_names[0]).to_numpy()[start::]	

	"""
	normalizeWord - Reemplaza los caracteres según los datos de la variable __replace.

	:string word: palabra a normalizar
	:returns: word normalizado (según los caracteres de la variable __replace)
	"""
	def normalizeWord(word):
		for v, n in SocratesReader.__replace:
			word = word.replace(v, n)
		return word

	"""
	loadParalelo - Carga los datos de los alumnos de un paralelo en un diccionario cuyos valores son pares rol, lista con las palabras que componen el nombre de un alumno.

	:lista data: lista con los datos del excel del paralelo
	:returns: diccionario cuyos valores son pares rol, lista con las palabras que componen el nombre de un alumno.
	"""
	def loadParalelo(data):
		nombres = {}	
		for rol, nombre, app, apm in data[:, [1, 7, 6, 5]]:
			nombres[rol] = [SocratesReader.normalizeWord(word) for word in [j for i in map(mc('split', " "), [nombre.lower(), app.lower(), apm.lower()]) for j in i]]

		return nombres

	"""
	loadSocrates - Carga los nombres de los alumnos de un archivo Sócrates en una lista de listas donde cada elemento de éstas últimas son las palabras que componen el nombre del alumno.

	:lista data: lista con los datos del excel de Sócrates
	:returns: lista de listas con las palabras que componen el nombre del alumno
	"""
	def loadSocrates(data):
		nombres = []
		for nombre in data[:-1, 0]:
			nombre = SocratesReader.normalizeWord(nombre).lower()
			nombres.append([word for word in nombre.split()])

		return nombres


	"""
	wordBreak - Determina si un string puede separarse en una o más palabras de un "diccionario", en este caso, sirve para determinar que YerkoMarillan es Yerko Marillan.

	:string nombre: nombre a romper
	:list diccionario: palabras que componen un nombre
	:returns: True si es posible separar la palabra en palabras del diccionario, False en caso contrario
	"""
	def wordBreak(nombre, dicc):
		sLen = len(nombre)
		possible = [False for i in range(sLen + 1)]
		possible[0] = True

		for i in range(sLen):
			for j in range(i + 1):
				if possible[j] and nombre[j:i + 1] in dicc:
					possible[i + 1] = True
					break;

		return possible[sLen]

	"""
	intersectData - Realiza la intersección entre los datos del excel de Paralelos y el excel de Sócrates

	:array socrates: arreglo de loadSocrates
	:array paralelo: arreglo de loadParalelo
	:returns: diccionario de partes rol, lista cuyos elementos son las palabras que componen el nombre del alumno en el excel de Sócrates y en el del Paralelo
	"""
	def intersectData(socrates, paralelo):
		r = {}
		last = []
		for nombres in socrates:
			if len(nombres) == 1:
				last.append(nombres)
				# Los nombres de 1 palabra quedan para el final
			else:
				for rol, palabras in paralelo.items():
					i = 0
					for nombre in nombres:
						if nombre in palabras:
							i += 1

						if i >= 2:
							r[rol] = [nombres, palabras]
							break
		
		#Nombres de una palabra
		for nombres in last:
			for rol, palabras in paralelo.items():
				if SocratesReader.wordBreak(nombres[0], palabras):
					if rol not in r:
						r[rol] = [nombres, palabras]
						break

		return r
