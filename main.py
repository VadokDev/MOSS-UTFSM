# -*- coding: UTF-8 -*-

import sys
import json
import pathlib

from moss import Moss
from alumnosreader import AlumnosReader as ar
from datetime import datetime as dt
from os import listdir, path, walk
from bs4 import BeautifulSoup
from xlwt import Workbook
from zipfile import ZipFile

# This is technically the best way to do it...
# See https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string


def sanitize(word):
    return word.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


userId = int(sys.argv[1])
similarityPercent = int(sys.argv[6])
PATH_INPUT_FILES = path.join(
    ".", "files", sys.argv[2], sys.argv[3], sys.argv[4], "Students", "xls")
PATH_OUTPUT_FILES = path.join(
    ".", "files", sys.argv[2], sys.argv[3], sys.argv[4], "Students", "json")
PATH_HOMEWORK_FILES = path.join(
    ".", "files", sys.argv[2], sys.argv[3], sys.argv[4], "Homeworks", sys.argv[5])
pathlib.Path(PATH_OUTPUT_FILES).mkdir(parents=True, exist_ok=True)
pathlib.Path(path.join("results", sys.argv[5])).mkdir(
    parents=True, exist_ok=True)
fileList = [f for f in listdir(PATH_INPUT_FILES) if path.isfile(
    path.join(PATH_INPUT_FILES, f))]

print("Creating JSON files for student sections")

for fileName in fileList:
    if fileName.startswith("."):
        continue

    result = {}
    section = fileName.split('_')[2]
    file = open(path.join(PATH_OUTPUT_FILES, section + ".json"), 'w')

    print("Loading student's data from the section:", section)
    for id, rol, dv, rut, _, app, apm, nombre, _, carrera, email in ar.loadFile(path.join(PATH_INPUT_FILES, fileName), ar.START_INDEX_PARALELO):
        nombreFinal = nombre.split()[0]+" "+app+" "+apm

        if dv == 'K' or dv == 'k':
            dv = "11"

        if dv != dv or email != email or rol != rol:
            continue

        result[rut] = {
            'rol': rol,
            'nombre': nombreFinal.title(),
            'email': email,
            'carrera': carrera
        }

    json.dump(result, fp=file, ensure_ascii=False)
    file.close()

print("Extracting all zip files")

for root, dirs, files in walk(PATH_HOMEWORK_FILES):
    for file in files:
        if file.endswith(".zip"):
          with ZipFile(path.join(root, file), 'r') as zipObj:
             zipObj.extractall(path=root)

print("Uploading homeworks to MOSS")

m = Moss(userId, "python")
m.addFilesByWildcard(PATH_HOMEWORK_FILES + "/*/*")
url = m.send()
print("Downloading report URL: " + url)
m.saveWebPage(url, PATH_HOMEWORK_FILES + "/report.html")

json_text_list = {}
for file in listdir(PATH_OUTPUT_FILES):
    with open(path.join(PATH_OUTPUT_FILES, file)) as json_file:
        if file.endswith('.json'):
            json_text_list[file.split(".")[0]] = json.load(json_file)

mossReport = BeautifulSoup(
    open(path.join(PATH_HOMEWORK_FILES, "report.html")), features="lxml")
table = mossReport.find_all('table')[0]

wb = Workbook()
excelFile = wb.add_sheet(sys.argv[4])

excelFile.write(0, 0, 'Nombres')
excelFile.write(0, 1, 'Apellidos')
excelFile.write(0, 2, 'ROL')
excelFile.write(0, 3, 'RUT')
excelFile.write(0, 4, 'Paralelo')
excelFile.write(0, 5, '% de Copia')
excelFile.write(0, 6, ' - ')
excelFile.write(0, 7, 'Nombres')
excelFile.write(0, 8, 'Apellidos')
excelFile.write(0, 9, 'ROL')
excelFile.write(0, 10, 'RUT')
excelFile.write(0, 11, 'Paralelo')
excelFile.write(0, 12, '% de Copia')
excelFile.write(0, 13, 'Líneas Similares')
excelFile.write(0, 14, 'URL')

linea = 1

for row in table.find_all("tr")[1:]:
    cells = row.find_all("td")
    url = cells[0].find_all("a", href=True)[0]['href']

    f1 = cells[0].text.split("/")[7:]
    f2 = cells[1].text.split("/")[7:]

    name1 = f1[0].split("_")[:-4]
    name2 = f2[0].split("_")[:-4]

    p1 = int(f1[1].split("%")[0].split("(")[-1])
    p2 = int(f2[1].split("%")[0].split("(")[-1])

    if p1 >= similarityPercent and p2 >= similarityPercent:

        n1 = name1
        n2 = name2
        paralelo1 = 0
        paralelo2 = 0
        nombre1 = ""
        nombre2 = ""
        rol1 = ""
        rol2 = ""
        rut1 = ""
        rut2 = ""

        for p in json_text_list:
            for a in json_text_list[p].items():
                if sanitize(n1[0]) in sanitize(a[1]["nombre"]) and sanitize(n1[-1]) in sanitize(a[1]["nombre"]):
                    nombre1 = a[1]["nombre"]
                    paralelo1 = p
                    rol1 = a[1]["rol"]
                    rut1 = a[0]

        for p in json_text_list:
            for a in json_text_list[p].items():
                if sanitize(n2[0]) in sanitize(a[1]["nombre"]) and sanitize(n2[-1]) in sanitize(a[1]["nombre"]):
                    nombre2 = a[1]["nombre"]
                    paralelo2 = p
                    rol2 = a[1]["rol"]
                    rut2 = a[0]

        if nombre1 == "":
            nombre1 = ["Student", "not found", "", ""]
        if nombre2 == "":
            nombre2 = ["Student", "not found", "", ""]

        #print("Alumno 1:", nombre1, "P" + str(paralelo1), "-", "Alumno 2:", nombre2, "P" + str(paralelo2) + ". Líneas:", l)
        excelFile.write(linea, 0, " ".join(n1[:2]))
        excelFile.write(linea, 1, " ".join(n1[2:]))
        excelFile.write(linea, 2, rol1)
        excelFile.write(linea, 3, rut1)
        excelFile.write(linea, 4, paralelo1)
        excelFile.write(linea, 5, p1)
        excelFile.write(linea, 6, ' - ')
        excelFile.write(linea, 7, " ".join(n2[:2]))
        excelFile.write(linea, 8, " ".join(n2[2:]))
        excelFile.write(linea, 9, rol2)
        excelFile.write(linea, 10, rut2)
        excelFile.write(linea, 11, paralelo2)
        excelFile.write(linea, 12, p2)
        excelFile.write(linea, 13, int(cells[2].text))
        excelFile.write(linea, 14, url)
        linea += 1

        #print(nombre1 + "\t" + str(paralelo1) + "\t" + nombre2 + "\t" + str(paralelo2) + "\t" + str(p1)+"%"+ "\t" + str(p2)+"%" + "\t" + cells[2].text)

wb.save(path.join("results", sys.argv[5], sys.argv[5] +
                  " - " + dt.now().strftime("%Y-%M-%d %H%M%S") + ".xls"))
