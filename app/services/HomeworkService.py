from os import path, walk, makedirs
from zipfile import ZipFile
from tarfile import open as TarFile
from app.utils.FileUtils import copyEntireFolder


class HomeworkService:
    def __init__(self, courseFolder, homework):
        self.dbName = courseFolder
        self.dbPath = path.join("data", self.dbName, homework)
        self.homework = homework

    def getResultsFolder(self):
        return path.join("data", self.dbName, "results", self.homework)

    def getWebResultsFolder(self, uuid):
        return path.join("data", self.dbName, "results", self.homework, "web")

    def getAll(self):
        for root, dirs, files in walk(self.dbPath):
            for fileName in files:
                if (
                    fileName.endswith(".zip")
                    or fileName.endswith(".rar")
                    or fileName.endswith(".tar")
                    or fileName.endswith(".gz")
                ):
                    continue
                yield path.join(root, fileName)

    def decompressAll(self):
        for root, dirs, files in walk(self.dbPath):
            for fileName in files:
                self.decompressFile(root, fileName)

    def decompressFile(self, directory, fileName):
        filePath = path.join(directory, fileName)
        if filePath.endswith(".zip"):
            with ZipFile(filePath, "r") as zipObj:
                zipinfo = zipObj.infolist()
                for member in zipinfo:
                    member.filename = str(bytes(member.filename,'utf-8').decode('utf-8','ignore').encode('utf-8'))
                    zipObj.extract(member, directory)
        elif filePath.endswith(".tar.gz"):
            tar = TarFile(filePath, "r:gz")
            tar.extractall(path=directory)
            tar.close()
        elif filePath.endswith(".tar"):
            tar = TarFile(filePath, "r:")
            tar.extractall(path=directory)
            tar.close()

    def sortHomeworks(self, results, directory, fileName):
        for section in results:
            sectionFolder = path.join(directory, section)

            if not path.exists(sectionFolder):
                makedirs(sectionFolder)

            for result in results[section]:
                if section == "inter":
                    folderName = (
                        result["student1"]["section"]
                        + " "
                        + result["student1"]["name"]
                        + " - "
                        + result["student2"]["section"]
                        + " "
                        + result["student2"]["name"]
                    )
                else:
                    folderName = (
                        result["student1"]["name"] + " - " + result["student2"]["name"]
                    )
                resultFolder = path.join(sectionFolder, folderName).replace(" .", "")

                if not path.exists(resultFolder):
                    makedirs(resultFolder)

                folder1 = path.join(
                    resultFolder,
                    result["student1"]["section"] + " " + result["student1"]["name"],
                ).replace(" .", "")

                if not path.exists(folder1):
                    makedirs(folder1)

                folder2 = path.join(
                    resultFolder,
                    result["student2"]["section"] + " " + result["student2"]["name"],
                ).replace(" .", "")
                
                if not path.exists(folder2):
                    makedirs(folder2)

                copyEntireFolder(result["dir1"], folder1)
                copyEntireFolder(result["dir2"], folder2)
