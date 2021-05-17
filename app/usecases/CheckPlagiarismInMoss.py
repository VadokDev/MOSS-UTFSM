from uuid import uuid4


class CheckPlagiarismInMoss:
    def __init__(self, homeworkService, mossService, studentService):
        self.homeworkService = homeworkService
        self.mossService = mossService
        self.studentService = studentService

    def start(self, sPercent, homeworkName, reportUrl=False):
        self.homeworkService.decompressAll()
        students = self.studentService.getAll()
        for homework in self.homeworkService.getAll():
            self.mossService.addFile(homework)

        reportFolder = self.homeworkService.getResultsFolder()
        reportUuid = str(uuid4())
        reportWebFolder = self.homeworkService.getWebResultsFolder(reportUuid)

        if not reportUrl:
            reportUrl = self.mossService.send()

        print("Reporte MOSS:", reportUrl)
        self.mossService.download_report(
            reportUrl,
            reportWebFolder,
            4,
            on_read=lambda url: print("*", end="", flush=True),
        )

        reportData = self.mossService.parseReport(reportWebFolder, "index.html")
        results = {}
        for plagio in reportData:
            if plagio["simPercent1"] < sPercent and plagio["simPercent2"] < sPercent:
                continue

            student1 = self.studentService.findStudentByName(
                plagio["student1"], students
            )
            student2 = self.studentService.findStudentByName(
                plagio["student2"], students
            )

            section = "inter"
            if student1["section"] == student2["section"]:
                section = student1["section"]
            elif student1["section"] == "not found" or student2["section"] == "not found":
                section = "not found"

            if section not in results:
                results[section] = []

            results[section].append(
                {
                    "student1": student1,
                    "student2": student2,
                    "simPercent1": plagio["simPercent1"],
                    "simPercent2": plagio["simPercent2"],
                    "lines": plagio["lines"],
                    "dir1": plagio["dir1"],
                    "dir2": plagio["dir2"],
                    "url": "http://moss-utfsm.s3.fr-par.scw.cloud/"
                    + reportUuid
                    + "/"
                    + plagio["url"],
                }
            )

        self.studentService.generateReport(results, reportFolder, homeworkName)
        self.homeworkService.sortHomeworks(results, reportFolder, homeworkName)
        self.mossService.uploadReport(reportWebFolder, reportUuid)
        print(
            "MOSS Url: http://moss-utfsm.s3.fr-par.scw.cloud/"
            + reportUuid
            + "/index.html"
        )
