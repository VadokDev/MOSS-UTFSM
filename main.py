# -*- coding: UTF-8 -*-

import sys
from app.services.StudentService import StudentService
from app.services.HomeworkService import HomeworkService
from app.services.MossService import MossService
from app.usecases.CheckPlagiarismInMoss import CheckPlagiarismInMoss
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 5:
    print(
        "Usage: python main.py [Language] [CourseFolder] [Homework] [SimilarityPercent] [MOSS_URL|'']"
    )
    print("Example: python main.py python CSJ-IWI131-2021-01 T1 60")
    exit()

if len(sys.argv) < 6:
    _, language, courseFolder, homework, sPercent = sys.argv
    url = False
else:
    _, language, courseFolder, homework, sPercent, url = sys.argv
mossService = MossService(language)
studentService = StudentService(courseFolder)
homeworkService = HomeworkService(courseFolder, homework)

checkPlagiarismInMoss = CheckPlagiarismInMoss(
    homeworkService, mossService, studentService
)
checkPlagiarismInMoss.start(int(sPercent), homework, url)
