# :mortar_board: MOSS Client for the Programming Course of the UTFSM

**MOSS-UTFSM** is a tool that aims to support teachers of the Universidad Técnica Federico Santa María in the detection of plagiarism in homeworks, using the [Standford's MOSS System](https://theory.stanford.edu/~aiken/moss/ "Standford's Plagiarism Detection") for Measure Of Software Similarity.

## :mag_right: Requeriments

* Python 3.8 or latest
* Pyenv - [https://github.com/pypa/pipenv](https://github.com/pypa/pipenv)
* MOSS User ID - [Registering for Moss](https://theory.stanford.edu/~aiken/moss/)

## :floppy_disk: Installation

1. Clone this repository

    ```git clone https://github.com/VadokDev/MOSS-UTFSM```

2. Install required packated

    ```pipenv install```

## :snake: Usage

1. Put student lists (.xls) in ```./files/[Year-Semester]/[Course]/[Campus]/Students/xls```
	* Example: `./files/2020-01/IWI-131/CSJ/xls`
		* **Year**: 2020
		* **Semester**: 01
		* **Course**: IWI-131
		* **Campus**: CSJ

2. Download from AULA the student howeworks zip file and extract it in ```./files/[Year-Semester]/[Course]/[Campus]/Homeworks/[HomeworkName]```
	* Example: `./files/2020-01/IWI-131/CSJ/T3`
		* **Year**: 2020
		* **Semester**: 01
		* **Course**: IWI-131
		* **Campus**: CSJ
		* **Homework**: T3

3. Run the client using Pipenv
	```pipenv run python main.py [MOSS userId] [Year-Semester] [Course] [Campus] [HomeworkName] [Similarity %]```
	* Example: `pipenv run python main.py 123456789 2020-01 IWI-131 CSJ T3 60`
		* **Year**: 2020
		* **Semester**: 01
		* **Course**: IWI-131
		* **Campus**: CSJ
		* **HomeworkName**: T3
		* **Similarity %**: 60

4. Go to `./results/[HomeworkName]` and open the `[HomworkName] [Timestamp].xls` file, it has the students detected by MOSS with more than `[Similarity %]`

## :memo: To-Do List
* Make the program easier to use
* Improve the code (sorry, it's awful)
* Group same students in just one row
* Charts
* Improve this README (any suggestion is welcome)
* *Improve my english* (any suggestion is welcome x2)

## :star: Acknowledgements

* [@soachishti](https://github.com/soachishti) - For his [moss.py](https://github.com/soachishti/moss.py) interface for MOSS
* [Stantord University](https://www.stanford.edu/) - [MOSS](https://theory.stanford.edu/~aiken/moss/) developers & maintainers

## :unlock: License

This project is licensed under the MIT License - see the LICENSE file for details


