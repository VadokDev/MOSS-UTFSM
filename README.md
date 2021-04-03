# :mortar_board: MOSS Client for the Programming Course of the UTFSM

**MOSS-UTFSM** is a tool that aims to support teachers and assistants of the Universidad Técnica Federico Santa María in the detection of plagiarism in homework, using [Standford's MOSS System](https://theory.stanford.edu/~aiken/moss/ "Standford's Plagiarism Detection") for Measure Of Software Similarity and the [Amazon S3 Service](https://aws.amazon.com/s3/) for plagiarism reports storage.

## :mag_right: Requirements

* Python 3 or latest
* MOSS User ID, you can get one [here](https://theory.stanford.edu/~aiken/moss/)
* [Amazon S3 Bucket](https://aws.amazon.com/s3/) for plagiarism reports storage

## :floppy_disk: Installation

1. Clone this repository and navigate into it

    ```git clone https://github.com/VadokDev/MOSS-UTFSM```
    
    ```cd MOSS-UTFSM```

2. Rename the .env.example file to .env
3. Configure environment variables in the .env file
    * MOSS_ID=
    * ENDPOINT_URL=
    * AWS_ACCESS_KEY_ID=
    * AWS_SECRET_ACCESS_KEY=
    * REGION_NAME=

3. Install dependences from requirements.txt (it's recommended to use [Virtual Environments](https://docs.python.org/3/tutorial/venv.html))

    ```pip install -r requirements.txt```

## :snake: Usage

1. Create a new Course folder inside ```data``` to store the students and homework files, for example, ```CSJ-INF131-2021-01```
2. Create a ```students``` folder inside the Course folder and put the [SIGA](https://siga.usm.cl/) exported students lists (.xls) in it, for example, ```data/CSJ-INF131-2021-01/students```.
2. Download from [AULA](https://aula.usm.cl/) the student howeworks zip file and extract it in a new folder with the homework's name inside the folder created in step 1, for example, ```data/CSJ-INF131-2021-01/T1```. 
3. Run the program with 
	
    ```python main.py [Language] [CourseFolder] [Homework] [SimilarityPercent]```
	
    Where:
    * Language: the programming language used for plagiarism detection; see available list in [MossService.py](/app/services/MossService.py#L17-L43)
    * CourseFolder: name of the folder created in ```data``` for store student and homework files
    * Homework: name of the homework folder in the CourseFolder
    * SimilarityPercent: % of similarity between two homework to classify them as plagiarism
    
    Example: ```python main.py python CSJ-INF131-2021-01 T1 60```
    
4. Copy the MOSS URL output; that URL stores the complete MOSS plagiarism report. 

5. Go to the ```results``` folder inside the Course folder and open the folder with the name of the homework used (for example. ```data/CSJ-INF131-2021-01/results/T1```), here you'll find:
	* web/: folder with the entire MOSS report website
	* [section]/: folder with the high similarity homework of students in [section] (example: Section 201 students)
	* inter/: folder with the high similarity homework of students from different sections
	* not found/: folder with the high similarity homework of students that weren't found in the students .xls files
	* [homework] [timestamp].xls: excel report with the detail of high similarity homework and their students.
	
## :memo: To-Do List
* ~~Make the program easier to use~~
* ~~Improve the code (sorry, it's awful)~~
* Add testing
* Add a web interface
* Group same students in just one row
* Charts
* Improve this README (any suggestion is welcome)
* *Improve my english* (any suggestion is welcome x2)

## :star: Acknowledgments

* [@soachishti](https://github.com/soachishti) - For his [moss.py](https://github.com/soachishti/moss.py) interface for MOSS
* [@cristiancs](https://github.com/cristiancs) - For help me implementing the plagiarism report storage on Amazon S3 
* [Stanford University](https://www.stanford.edu/) - [MOSS](https://theory.stanford.edu/~aiken/moss/) developers & maintainers

## :unlock: License

This project is licensed under the MIT License - see the LICENSE file for details.


