from pandas import ExcelFile
from os import path
from xlwt import Workbook, Style
from datetime import datetime
from app.utils.FileUtils import getFileNames, getFileNameSection, sanitize


class StudentService:
    def __init__(self, courseFolder):
        self.dbName = courseFolder
        self.dbPath = path.join("data", self.dbName, "students")

    def getAll(self):
        students = {}

        for fileName in getFileNames(self.dbPath):
            if fileName.startswith('.'):
                continue
            section = getFileNameSection(fileName)
            file = ExcelFile(path.join(self.dbPath, fileName))
            for (
                rol,
                rut,
                lastname1,
                lastname2,
                names,
                career,
                email,
            ) in self.studentsExcelToList(file, 8):
                name = " ".join([names, lastname1, lastname2]).upper()
                students[rut] = {
                    "rol": rol,
                    "name": name,
                    "names": names.upper(),
                    "lastnames": " ".join([lastname1, lastname2]).upper(),
                    "rut": rut,
                    "career": career,
                    "email": email,
                    "section": section,
                }

        return students

    def studentsExcelToList(self, fileName, startIndex):
        file = ExcelFile(fileName)
        studentsRawData = file.parse(file.sheet_names[0]).to_numpy()[startIndex::]
        for student in studentsRawData:
            yield [
                student[1],
                student[3],
                student[5],
                student[6],
                student[7],
                student[9],
                student[10],
            ]

    def findStudentByName(self, name, students):
        for student in students.values():
            matchs = 0
            for i in sanitize(name).split():
                if i in sanitize(student["name"]).split():
                    matchs += 1
            if matchs >= 3:
                return student
        return self.getNotFoundStudent(name)

    def getNotFoundStudent(self, name):
        return {
            "rol": "-",
            "name": name,
            "names": name.upper(),
            "lastnames": "-",
            "rut": "-",
            "career": "-",
            "email": "-",
            "section": "not found",
        }

    def mapResultToReport(self, result):
        res = [
            result["student1"]["names"],
            result["student1"]["lastnames"],
            result["student1"]["rol"],
            result["student1"]["rut"],
            result["student1"]["career"],
            result["student1"]["section"],
            result["simPercent1"],
            "",
            result["student1"]["names"],
            result["student1"]["lastnames"],
            result["student1"]["rol"],
            result["student1"]["rut"],
            result["student1"]["career"],
            result["student1"]["section"],
            result["simPercent1"],
            result["lines"],
            result["url"],
        ]
        return res

    def generateReport(self, students, directory, name):
        wb = Workbook()
        report = wb.add_sheet(name)
        bold = Style.easyxf("font: bold on;")

        headers = [
            "Nombres",
            "Apellidos",
            "ROL",
            "RUT",
            "Carrera",
            "Paralelo",
            "% de Copia",
            "",
            "Nombres",
            "Apellidos",
            "ROL",
            "RUT",
            "Carrera",
            "Paralelo",
            "% de Copia",
            "Lineas Similares",
            "MOSS File",
        ]

        for column, header in enumerate(headers):
            report.write(0, column, header, bold)

        row = 1
        for results in students.values():
            for result in results:
                for column, value in enumerate(self.mapResultToReport(result)):
                    report.write(row, column, value)
                row += 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        fileName = name + " " + timestamp + ".xls"
        filePath = path.join(directory, fileName)
        wb.save(filePath)
