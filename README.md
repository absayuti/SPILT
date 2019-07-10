# SPILT
SPI (structured programming and interfacing course) Lab Test

SPILT started as a collection of BASH scripts. Each so-called command is a BASH script with an obviously named file such as view, submit, help and view As the needs grew, a python program was developed so that more features can be added from time to time.

________________________________________________________________________________
For Instructor

1.	Prepare questions in a plain text files in the following format:

	<QUESTION>
	Contents of question #1 …
	Can be more than one line but Be careful to limit each line to
	about 79 to 80 characters per line.

	Some white spaces may be stripped when displayed. So you may need to
	write like this (using an underscore at the beginning of a line):
	_                                                        [x marks]
	</QUESTION>

	<QUESTION>
	This is the next question, ie #2. Questions are automatically numbered
	according to the order they are placed. Do not need to specify question
	number. Total number of question will be automatically calculated. But
	total marks is not (yet).
	_                                                         [x marks] 
	</QUESTION>

2.	Save the file with names as the following guidelines:

	Assessment type		Question#	File name
	Assignment 1		1		Qasgn11.txt
				2		Qasgn12.txt
	Assignment 2		1		Qasgn21.txt
				2		Qasgn22.txt
	Lab Test 1		1		Qtest11.txt
				2		Qtest12.txt
	Lab Test 2		1		Qtest21.txt
				2		Qtest22.txt
				3		Qtest23.txt

3.	Copy question files into (or replace the existing one on) /srv/pub/spilt/

4.	Test setup by using this command:        

	/mnt/pub/spilt/spiltXXX.py
	

________________________________________________________________________________
For Student, these are the steps:

1.	Start Linux.

2.	Open a terminal window.

3.	Enter command:   labtest

	(There should be a request to enter your student ID)

4.	Enter your student ID

	(The program will search for your ID and if found will display your name, 
	the number of questions to be answered, and a list of commands available)

5.	Press [Enter] key to view the first question

	(The first question should be displayed followed by a short list of valid 
	commands)

6.	Type E and press [Enter] to create/edit your program (to answer the question)

	(gedit editor will be opened in another window. Text for the current 
	question will be appear in the top comment section of your program)

7.	Write your program and save it when you are ready to compile it

8.	Select the SPILT terminal window. Enter C to compile your program

9.	If you need to make any correction, repeat steps 6 to 8.

10.	If your program is compiled successfully, execute it to test its output by
	entering R or run.

11.	When you are satisfied with your answer (program), enter S to submit your 
	program to the server (you'll be prompted for your program's filename)

12.	Enter the filename of your program

	(If valid filename was entered, the file will be transferred to the server, 
	and you'll advance to the next question)

13.	Repeat steps 6 to 12 until all questions are answered.

15.	To close the terminal window, enter this command: exit


Summary of commands
```````````````````
	Step			Command		Remarks
	Start test		labtest		Enter this at the terminal command prompt
	Display help		help		Display the help screen which briefly describes 
								the commands available to the user
	View question		view		Display current question
	Edit program		edit		Start writing a C program to answer the question
						or to continue editing the current C program.
						gedit editor will be opened in a new window
						(if it is not already opened) containing the C
						program you are writing for the current
						question. The program file is automatically
						named according the the question number, i.e.
						program1.c for question 1, program2.c for
						question 2 etc.
	Compile			compile		Compile the C program (created above) using gcc
	Verify			run		Run the program (when compilation is successful)
						Repeat any of the steps above until satisfied 
						with the answer.
	Submit program		submit		Submit the answer/program to server. If there 
						are more questions to answer it will increment 
						to the next question number.

________________________________________________________________________________
Important files on the server

The following files must be placed in designated locations:

	LOCATION		FILES			REMARKS
	
	/srv/pub/spilt/		spilt.XXX.py		The python script i.e. the main program
	
				studentlist.txt		Student names
					
				Qasgn11.txt		The question banks
				Qasgn12.txt
				Qasgn21.txt
				Qasgn22.txt
				Qasgn31.txt
				Qasgn32.txt
				Qtest11.txt
				Qtest12.txt
				Qtest13.txt
				Qtest21.txt
				Qtest22.txt
				Qtest23.txt
					
	/srv/xfr/spilt/a1	n/a			Subdirectory for answer files				
	/srv/xfr/spilt/a2	n/a					"
	/srv/xfr/spilt/a3	n/a					"
	/srv/xfr/spilt/t1	n/a					"
	/srv/xfr/spilt/t2	n/a					"

________________________________________________________________________________
Known issues (unknown fixes?)

1.	Access can get very slow when multiple clients accessing the program/script/
	files concurrently. Maybe it has something to do with NFS. In the program
	itself, file access time has been meinimized by reading the whole file 
	and buffering it in a list.
	
	It seems that the 'first-time' access is the slowest one. That's whay NFS is
	suspected to be the issue.


________________________________________________________________________________
To do:

	*	FIX problem of using tee to redirect outputs (on hold)
	* 	status file - + student id, hostname 
	* 	timestamp sync with server? is it possible?

Done:
	x   	Add option/format for in-class assignment (2 parts)
	x 	Modify test --> 2 parts too
	x	Revert to fixed number of of Q files, pick random Q index from file
	x	Input prompt has timeout. Will update time lapsed every 10 seconds
	x	Check time left/over before displaying question
	x	Submit last program (programX.c) when over time limit
	x	Fixed bug: order of question not always OK.	The array qfileset is
		sorted() after the file list is retreived
	x	Fixed bug when compiling with gcc: -lm moved to end of command text
	x	Allow viewing of questions only
	x	Changed the function to verify ID so that the file content is buffered
	    	into a list[], then comparison is done with the list. This should
	    	speed up concurrent access time.
	x 	Refixed the start time when program stopped half-way. Now it reads the
		first time-stamp in the status file instead of the one on the last line
	x	Changed duration oaf assignments to 45 minutes instead of 30
	x	Hide the subdirectory where the files are transferred to, i.e.
	    	/mnt/xfr/XX/.NNNNN, where XX = a1, a2, a3, t1,t2; and NNNNN is the 
	    	matric number
	x	The settings are now stored in dicts

