from socket import socket as Socket
from os import path, makedirs, getenv
from threading import Thread
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import boto3
from botocore.exceptions import ClientError
from app.utils.FileUtils import getFileNames

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


class MossService:
    languages = (
        "c",
        "cc",
        "java",
        "ml",
        "pascal",
        "ada",
        "lisp",
        "scheme",
        "haskell",
        "fortran",
        "ascii",
        "vhdl",
        "verilog",
        "perl",
        "matlab",
        "python",
        "mips",
        "prolog",
        "spice",
        "vb",
        "csharp",
        "modula2",
        "a8086",
        "javascript",
        "plsql",
    )
    server = "moss.stanford.edu"
    port = 7690

    def __init__(self, language="python"):
        self.user_id = getenv("MOSS_ID")
        self.bucket = getenv("BUCKET")
        self.options = {"l": "python", "m": 100, "d": 1, "x": 0, "c": "", "n": 150}
        self.base_files = []
        self.files = []
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=getenv("ENDPOINT_URL"),
            aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=getenv("REGION_NAME"),
        )

        if language in self.languages:
            self.options["l"] = language

    def setIgnoreLimit(self, limit):
        self.options["m"] = limit

    def setCommentString(self, comment):
        self.options["c"] = comment

    def setNumberOfMatchingFiles(self, n):
        if n > 1:
            self.options["n"] = n

    def setDirectoryMode(self, mode):
        self.options["d"] = mode

    def setExperimentalServer(self, opt):
        self.options["x"] = opt

    def addBaseFile(self, file_path, display_name=None):
        if path.isfile(file_path) and path.getsize(file_path) > 0:
            self.base_files.append((file_path, display_name))
        else:
            print("addBaseFile({}) => File not found or is empty.".format(file_path))

    def addFile(self, file_path, display_name=None):
        if path.isfile(file_path) and path.getsize(file_path) > 0:
            self.files.append((file_path, display_name))
        else:
            print("addFile({}) => File not found or is empty.".format(file_path))

    def getLanguages(self):
        return self.languages

    def uploadFile(self, s, file_path, display_name, file_id):
        if display_name is None:
            # If no display name added by user, default to file path
            # Display name cannot accept \, replacing it with /
            display_name = file_path.replace(" ", "_").replace("\\", "/")

        size = path.getsize(file_path)
        message = "file {0} {1} {2} {3}\n".format(
            file_id, self.options["l"], size, display_name
        )
        s.send(message.encode())
        with open(file_path, "rb") as f:
            s.send(f.read(size))

    def send(self):
        try:
            print("Submmiting files to MOSS")
            s = Socket()
            s.settimeout(5 * 60)
            s.connect((self.server, self.port))

            s.send("moss {}\n".format(self.user_id).encode())
            s.send("directory {}\n".format(self.options["d"]).encode())
            s.send("X {}\n".format(self.options["x"]).encode())
            s.send("maxmatches {}\n".format(self.options["m"]).encode())
            s.send("show {}\n".format(self.options["n"]).encode())

            s.send("language {}\n".format(self.options["l"]).encode())
            recv = s.recv(1024)
            if recv == "no":
                s.send(b"end\n")
                s.close()
                raise Exception("send() => Language not accepted by server")

            for file_path, display_name in self.base_files:
                self.uploadFile(s, file_path, display_name, 0)

            index = 1
            for file_path, display_name in self.files:
                self.uploadFile(s, file_path, display_name, index)
                index += 1

            s.send("query 0 {}\n".format(self.options["c"]).encode())

            response = s.recv(1024)

            s.send(b"end\n")
            s.close()

            return response.decode().replace("\n", "")
        except OSError as e:
            print("5m timeout, retrying")
            return self.send()

    def saveWebPage(self, url, path):
        if len(url) == 0:
            raise Exception("Empty url supplied")

        response = urlopen(url)
        content = response.read()

        f = open(path, "w", errors="ignore")
        f.write(content.decode())
        f.close()

    def process_url(self, url, urls, base_url, directory, on_read):
        print("Processing URL: " + url)
        response = urlopen(url)
        html = response.read()
        on_read(url)
        soup = BeautifulSoup(html, "lxml")
        file_name = path.basename(url)

        if (
            not file_name or len(file_name.split(".")) == 1
        ):  # Not file name eg. 123456789 or is None
            file_name = "index.html"

        for more_url in soup.find_all(["a", "frame"]):
            if more_url.has_attr("href"):
                link = more_url.get("href")
            else:
                link = more_url.get("src")

            if link and (link.find("match") != -1):  # Download only results urls
                link_fragments = link.split("#")
                link = link_fragments[0]  # remove fragment from url

                link_hash = ""
                if len(link_fragments) > 1:
                    link_hash = "#" + link_fragments[1]

                basename = path.basename(link)

                if basename == link:  # Handling relative urls
                    link = base_url + basename

                if more_url.name == "a":
                    more_url["href"] = basename + link_hash
                elif more_url.name == "frame":
                    more_url["src"] = basename

                if link not in urls:
                    urls.append(link)

        f = open(path.join(directory, file_name), "wb")
        f.write(soup.encode(soup.original_encoding))
        f.close()

    def download_report(self, url, directory, connections=4, on_read=lambda url: None):
        if len(url) == 0:
            raise Exception("Empty url supplied")

        if not path.exists(directory):
            makedirs(directory)

        base_url = url + "/"
        urls = [url]
        threads = []

        print("=" * 80)
        print("Downloading Moss Report - URL: " + url)
        print("=" * 80)

        # Handling thread
        for url in urls:
            t = Thread(
                target=self.process_url, args=[url, urls, base_url, directory, on_read]
            )
            t.start()
            threads.append(t)

            if len(threads) == connections or len(urls) < connections:
                for thread in threads:
                    thread.join()
                    threads.remove(thread)
                    break

        print("Waiting for all threads to complete")
        for thread in threads:
            thread.join()

    def parseReportStudent(self, text):
        name = text.split("/")[3].split("_")[:-5]
        percent = (
            text.split("/")[-1]
            .replace("(", "")
            .replace(")", "")
            .replace("%", "")
            .replace("_", "")
        )
        return {"name": " ".join(name), "percent": int(percent)}

    def getStudentDirectory(self, text):
        directory = "/".join(text.split("/")[:4])
        directory = (
            " ".join(directory.split("_")[:-4])
            + "_"
            + "_".join(directory.split("_")[-4:])
        )
        return directory

    def parseReport(self, reportFolder, reportHtmlFile):
        students = []
        reportPath = path.join(reportFolder, reportHtmlFile)
        mossFile = open(reportPath, encoding="UTF-8")
        mossReport = BeautifulSoup(mossFile, features="lxml")
        table = mossReport.find_all("table")[0]

        for row in table.find_all("tr")[1:]:
            firstUrl, secondUrl, linesCount = row.find_all("td")
            url = firstUrl.find_all(href=True)[0]["href"]
            student1 = self.parseReportStudent(firstUrl.text)
            dirStudent1 = self.getStudentDirectory(firstUrl.text)
            student2 = self.parseReportStudent(secondUrl.text)
            dirStudent2 = self.getStudentDirectory(secondUrl.text)
            students.append(
                {
                    "student1": student1["name"],
                    "simPercent1": student1["percent"],
                    "dir1": dirStudent1,
                    "student2": student2["name"],
                    "simPercent2": student2["percent"],
                    "dir2": dirStudent2,
                    "url": url,
                    "lines": int(linesCount.text),
                }
            )

        mossFile.close()
        return students

    def uploadReport(self, reportFolder, uuid):
        fileList = []
        for fileName in getFileNames(reportFolder):
            filePath = path.join(reportFolder, fileName)
            objectName = uuid + "/" + fileName
            fileList.append([filePath, objectName])

        pool = ThreadPool(processes=10)
        pool.map(self.uploadReportFile, fileList)

        return True

    def uploadReportFile(self, file):
        print("Uploading:", file[0])
        try:
            self.s3_client.upload_file(file[0], self.bucket, file[1])
        except Exception as exc:
            print("Error Uploading:", file[0], "msg:", exc)
        return True
