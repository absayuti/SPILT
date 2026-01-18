# SPILT
## Structured Programming And Interfacing Lab Test
AB Sayuti HM Saman Dec 2025

## 1.	Introduction

SPILT stands for “Structured Programming and Interfacing Lab Test”.  Structured Programming and Interfacing is an introductory programming course for fresh students at the Electrical and Electronic Engineering (EEE) Department of University of Technology PETRONAS (UTP).

SPILT started as a collection of BASH scripts to facilitate practical assessment (“lab test”) for students of ECB 1063 Structured Programming and Interfacing. Practical assessment is a very important evaluation method for the course as it tests the students on their programming skill in solving programming problems. SPILT allows lab tests to be conducted in the EEE’s Programming Laboratory, on about 30 PCs, and the answers submitted to a single location on a file server. SPILT allows an instructor to write a set of questions (programming problems) and each student has to answer the question one by one in particular order they are presented.

During a lab test, each question will be displayed on the PC’s screen. The answer written by a student is in the form of C program source code that the student writes, edits and tests it himself. He can write and edit his program as he would normally do when he was doing his programming exercises during programming lab sessions. When he is satisfied with his answer, he must submit his program to the file server before he can move on to the next question.

In its current form SPILT consists of a Python program, several text files that contain the data and a couple of BASH scripts to start various things. The main SPILT program is run from a shared subdirectory on an NFS (Network File System) server. Basically, SPILT is a Network-Hosted Executable where execution is primarily done on the clients. On the server, besides hosting the main program and data, a small socket service is run. This socket service is responsible for receiving files that the students send from the clients.
 
In the same subdirectory as SPILT, there are the data text files which contain programming problems, basically a set of question banks. SPILT displays selected questions from the question banks for a student to view, allows him to edit, compile and run a C program; and submit it to the server. SPILT also manages the order of which the questions progress and also keeps track of the duration and time limit of a lab test session.

## 2. Setting up SPILT
The basic setup of SPILT consists of a Linux server OS and several PCs as clients. As of this document, setup has been done successfully on Ubuntu Linux 12, 18 and 24. Other Linux should work as well. The server is set up as an NFS server and several script files are placed on the shared directories. The NFS shares are to be automatically mounted on the clients. The scripts are executed from the clients via the shared NFS directories.

### 2.1. Hardware and software
The hardware consists of a file server and about 30 PCs interconnected via local area network (LAN). The server shares two directories which are mounted to each client on startup. 

| HW & SW requirement | Directories and files |
|---|---|
| **Server** |
| x86_x64 CPU | /srv/pub/ – shared read only 
| 1 GB RAM     | /srv/pub/spilt/ – contains the main program, text of questions and student list
| 40 GB Hard disks | /srv/xfr/ – shared read/write – used for backup storage of students answers
| Ubuntu Server 10.04 
| NFS server installed
| **Client** | 
| x86_x64 CPU | /mnt/pub – mount point for /srv/pub/
| 512KB – 1GB RAM | /mnt/xfr – mount point for /srv/xfr/
| 40 GB Hard disk
| Ubuntu 12.04
| NFS client installed

### 2.2. Server setup
Setting up the server for SPILT is quite easy. Basically you only need to install NFS server service, create several subdirectories and copy a list of files into these subdirectories. The only thing to be careful about is the names and locations of the said files. The steps are as follows.

1. Install Ubuntu Server on the server. From experience, the desktop version will work equally well and is preferred most of the time because then it can be used as a workstation as well. The NFS service is not resource hungry nor intensive. It will be a waste if the server PC is only running one simple service. Besides, with the desktop GUI installed, you can work with multiple terminal windows. 

2. Setup NFS server service by entering the following commands. Do not type the $ sign – it is there to indicate that you are supposed to enter the command at the command prompt in a terminal:
``` 
	$ sudo apt update
	$ sudo apt install nfs-kernel-server
```
* To check if NFS server is running, use this command:
```	
	$ sudo systemctl status nfs-kernel-server
```
* Ubuntu will respond with several lines of text containing miscellaneous information. If the nfs-kernel-server is running, you should see words like Active: active (exited) or something similar.

* If the nfs-kernel-server service is not running, try restarting it with this command:
```
	$ sudo systemctl restart nfs-kernel-server 
```
3. Create the two subdirectories (pub and xfr) in the /srv directory, using these commands:
```
	$ sudo mkdir /srv/pub
	$ sudo mkdir /srv/xfr
```
* Make /srv/pub executable and read-only; and make /srv/xfr read-writable, like so:
```
	$ sudo chmod +rx /srv/pub
	$ sudo chmod +w /srv/xfr
``` 
4. Edit the /etc/exports file to set up sharing of the subdirectories. You can use your favorite text editor, but in this example we’ll use nano:
```	
	$ sudo nano /etc/exports
```
* In the /etc/exports file, add the following lines: 
```
	/srv/pub	197.19.27.0/24(ro,sync,no_subtree_check)
	/srv/xfr	197.19.27.0/24(rw,sync,no_subtree_check)
```
* Note: In the above example we assume that the server’s IP address is 197.19.27.50, thus within the subnet or local network 197.19.27.0. The entry 0/24 in the last number indicates the available range of the subnet from 197.19.27.1 to 197.19.27.254. Use your own network numbers as you see fit.

5.	Make two more subdirectories like so:
```
	$ sudo mkdir /srv/pub/spilt
	$ sudo mkdir /srv/pub/spilt/tools
```
* Copy all the files in the source “SPILT folder” into the /srv/pub/spilt/ subdirectory. The files are:
```
	spilt.NNNNN.py	- The program. NNNNN is the version number
	spilt.config	- Configuration file for SPILT
	runspilt.sh	    - BASH script that call spilt.NNNNN.py
	Qasgn*.txt		- Question banks for assignments. * = 11,12, 21, 22, 31,32
	Qtest*.txt		- Question banks for tests. * = 11,12, 13, 21, 22, 23
	Qsample*.txt	- Sample questions for practice. & = 1, 2
	Studentlist.txt	- List of student names. Format: 'matric# name'
	INSTALL.txt	    - Quick install instruction
	SPILT.docx		- A document similar to this but in docx format
```
6.	Copy the following files (from the SPILT folder) into the /srv/pub/spilt/tools/ subdirectory:
```   
	labtest                 - BASH script to be copied to the clients
	socksrv.recvfile.005.py - Python script to be run during every labtest session.
                              The name may vary slightly because this is always a work in progress
```
7.	The next step is to create a set of subdirectories to receive files via a socket server. First, create a subdirectory to denote the class or session in which the students are in. For example, if the class is “December 2025”, and let’s say we decide that ‘~/dec2025’ is the “class subdirectory”, then make it like so:
```
	$ sudo mkdir ~/dec2025
 ```
8. Then, create six more subdirectories inside the “class subdirectory” like so:
```
	$ mkdir ~/dec2025/asgn1
	$ mkdir ~/dec2025/asgn2
	$ mkdir ~/dec2025/asgn3
	$ mkdir ~/dec2025/labtest1
	$ mkdir ~/dec2025/labtest2
	$ mkdir ~/dec2025/practice
```
* Of course, if the “class subdirectory” is something other than ‘~/dec2025’, then use that name instead.

9. Then, copy the file socksrv.recvfile.005.py to the "class subdirectory”. The digits ‘005’ in the file is a 3-digit number denoting the version number of the script. So, it is possible to be 006, 007, 008 etc. This program is a socket server that needs to be run every time an assessment is in session. I think I have mentioned that before, but it doesn’t hurt to mention it again, is it? So, you can either copy the file from the source folder; or from the /srv/pub/spilt/tools/ subdirectory, like so:
```
$ sudo cp /srv/pub/spilt/tools/socksrv.recvfile.005.py ~/dec2025/.
```
* Of course, replace ‘dec2025’ with the actual “class subdirectory” name. But you already know that, don’t you? 

10.	In this step, you will be creating backup subdirectories under the /srv/xfr/ subdirectory. These subdirectories will be created as hidden subdirectories, hence a dot is added to its name. Enter these commands:
```
	$ sudo mkdir /srv/xfr/.a1
	$ sudo mkdir /srv/xfr/.a2
	$ sudo mkdir /srv/xfr/.a3
	$ sudo mkdir /srv/xfr/.t1
	$ sudo mkdir /srv/xfr/.t1
```
11.	Finally, run the socket server script like so (assuming the "class subdirectory” is ‘~/dec2025’):
```
	$ cd ~/dec2025			
	$ python3 socksrv.recvfile.005.py
```
* Now the server is ready to receive files from the client PCs.

### 2.3.	Client setup
These are the steps to set up a PC as a client. You will basically install Ubuntu, gedit text editor and gcc compiler; set it up as an NFS client, and copy over a short BASH script.
 
1.	Install Ubuntu OS on the client PC, if it is not already running Ubuntu.

2.	Install gedit text editor, like so:
```
	$ sudo apt update
	$ sudo apt install gedit
```
3.	Install gcc compiler, like so:
```
	$ sudo apt install gedit
```
4.	Setup NFS client service, like so:
```
$ sudo apt install nfs-common
```
5.	Test the availability of NFS shares from the server using the showmount command. For example if the server’s IP address is 197.19.27.50, then enter:
```
$ showmount -e 197.19.27.50
```
* If the NFS share is working, it will display something similar to this:
```
Export list for 192.19.27.50:
/srv/pub 192.19.27.0/24
/srv/xfr  192.19.27.0/24
```
6.	Edit the file /etc/fstab and add the following two entries:
```
197.19.27.50:/srv/pub  /mnt/pub nfs ro,_netdev,x-systemd.automount 0 0
197.19.27.50:/srv/xfr  /mnt/xfr nfs rw,_netdev,x-systemd.automount 0 0
```	
* Note 1: Replace 197.19.27.50: with the actual IP address of your server.
* Note 2: _netdev: Flags the filesystem as a network device, ensuring systemd waits for the network stack to be ready before attempting to mount it. x-systemd.automount: Instructs systemd to create an automount unit. Instead of mounting immediately, it sets up a placeholder mount point. The actual mount occurs only when something tries to access that directory.
* Note 3: On Ubuntu 18, the NFS shares may fail to mount, possibly due to timing issues during startup/mounting. Do the following:
		a) Create a file at: /etc/network/if-up.d/fstab with the following content:
```
#!/bin/sh
mount -a
```
		b) Make the file executable:
```		
	$ sudo chmod +x /etc/network/if-up.d/fstab
```
7.	Restart Ubuntu, like so:
```
	$ sudo reboot
```
8.	After the system is started, open a terminal and copy the file /mnt/pub/spilt/clienttools/labtest into /usr/bin subdirectory, like so:
```
	$ sudo cp /mnt/pub/spilt/clienttools/labtest /usr/bin/.
```
* Next, make the file labtest as read-only and executable, like so:
```
	$ sudo chmod +rx /usr/bin/labtest
```
9.	Test the installation by entering this command:
```
	$ labtest
```
* If everything is working correctly, the SPILT program will start. If things are not working as they are supposed to be, check that the shared subdirectories are available:
```
	$ ls /mnt
```
* If they are available, you should see something similar to this:
```
	pub  xfr
```
* If they are not available, it means that the NFS server is not working as intended. Try rebooting the server. If it still does not work, go through the procedure again. Reboot after each completed procedure and hope for the best.

### 2.4. Additional stuff

1.	During client startup, if the NFS shares were not correctly done e.g. wrong subdirectory names, wrong I.P. address etc., mounting of NFS shares may continue to fail even when corrections have been made. The NFS mount failure could be marked as “masked” as its status, which indicates that nfs-common has been intentionally disabled by the system. The service cannot start or be enabled in this state, preventing the mount from succeeding.

* To resolve this issue, the relevant systemd service needs to be unmasked and restarted:

* Check the NFS service status to verify that it is masked:
```
	$ sudo systemctl status nfs-common.service
```
* Look for keywords inactive(dead) and masked in the system’s response which indicates the service is indeed masked.

* Unmask the service:
```
	$ sudo systemctl unmask nfs-common.service
```
* Enable the service:
```
	$ sudo systemctl enable nfs-common.service
```
* Start the service:
```
	$ sudo systemctl start nfs-common.service
```
* If the above steps give an error, you need to delete the masked link manually:
```
	$ sudo rm /usr/lib/systemd/system/nfs-common.service
```
* Then repeat the above two steps.

* After the service is running, attempt NFS mount again, either manually or by using mount -a.
```
$ sudo mount -a
```
2.	The following command can be used to test the write speed when writing onto the NFS server.
```
	$ time dd if=/dev/zero of=/mnt/xfr/testfile bs=16k count=16384
```	
3.	Testing read speed when reading from the NFS server can be done with the following command:
```
	$ time dd if=/mnt/xfr/testfile of=/dev/null bs=16k 
```
## 3.	Using SPILT
### 3.1.	Instructions for Instructors
1.	For each class or batch of students, it is advisable to create a specific subdirectory to receive their answer files. Do not use previously used subdirectory for this purpose. The subdirectory should be created in the home directory on the SPILT server. For example if the class is for December 2025, you may want to use ‘dec2025’ as the name of the new “class subdirectory”, like so:
```
	$ mkdir ~/dec2025
```
2.	Next, make six subdirectories inside the newly created “class subdirectory”, like so:
```
	$ mkdir ~/dec2025/asgn1
	$ mkdir ~/dec2025/asgn2
	$ mkdir ~/dec2025/asgn3
	$ mkdir ~/dec2025/labtest1
	$ mkdir ~/dec2025/labtest2
	$ mkdir ~/dec2025/practice
```
3.	Then, copy the file receiver script into the “class subdirectory” so that you can easily start the socket service from within it. The command is (don’t miss the last dot):
```
	$ sudo cp /srv/pub/spilt/tools/socksrv.recvfile.005.py ~/dec2025/.
```
* The above steps (1 to 3) need to be done only once per each class or batch of students.

4.	Before each assessment session, please ensure that the content of the file /srv/pub/spilt/runspilt.sh is changed appropriately. The following command should open the file for editing:
```
	$ sudo nano /srv/pub/spilt/runspilt.sh 
```
* The content of the file should be similar to this:
```
#!/bin/bash
###############################################################################
# runspilt
#
# When run, this script will:
# - Ask user to choose (a) Asssessment (b) Practice run
# - Call the spilt python program
#
# Copy this file into /srv/pub/spilt
# Comment out commands that are not relevant
# Or modify as needed
# Ensure that it is executable (# chmod +x start)
#
###############################################################################

clear
echo "==============================================================================="
echo " =                       UNIVERSITI TEKNOLOGI PETRONAS                        ="
echo " =            Department of Electrical and Electronic Engineering             ="
echo " =              EDB1023 Structured Programming and Interfacing                ="
echo " =          (S)tructured (P)rogramming and (I)nterfacing (L)ab (T)est         ="
echo "==============================================================================="
echo
echo " Please enter one of the following options:"
echo 
while true; do
	echo "   1 = Assignment or Test"
	echo
	echo "   2 = Practice"
	echo
	read -p "  >" ans
    case $ans in
        [1] ) /mnt/pub/spilt/spilt.09400.py --t2; break;;
        [2] ) /mnt/pub/spilt/spilt.09400.py; break;;
        * ) echo " Please enter 1 or 2.";;
    esac
done

# Start SPILT for Assignment #1
# mnt/pub/spilt/spilt09400.py --a1
#
# Start SPILT for Assignment #2
# /mnt/pub/spilt/spilt09400.py --a2
#
# Start SPILT for Lab Test #1
# /mnt/pub/spilt/spilt09400.py --t1
#
# Start SPILT for Lab Test #1
# /mnt/pub/spilt/spilt09400.py --t2
#
```

5. The part of the script that needs to be changed is marked as bold red in the above figure, specifically: ‘spilt.09400.py --t2’. Most of the time the Python filename (‘spilt.09400.py’) need not be changed, unless some kind of upgrade or major correction has been done. The argument part (e.g. ‘-- t2’) however, need to indicate the correct assessment type/session. They are:
```
	spilt.09400.py --a1	- Assignment 1
	spilt.09400.py --a2	- Assignment 2
	spilt.09400.py --a3	- Assignment 3
	spilt.09400.py --t1	- Test 1
	spilt.09400.py --t2	- Test 2
```
* Make the appropriate changes and save the file.

6.	Then, run the “file receiver script”, like so:
```
	$ cd ~/dec2025			
	$ python3 socksrv.recvfile.005.py
```
7.	To test, run SPILT from a client PC. When a student ID is prompted, enter 0 (zero).

#### 3.1.1.	Question Banks
1.	The question banks for SPILT are spread into several files, so that they are easier to manage. There are three main types of questions i.e. assignments, tests and samples. These are indicated by their filenames i.e. Qasgn*.txt (for assignments), Qtest*.txt (tests) and Qsamples*.txt (sample questions for practice). Further, they are spread into different files for different question numbers. The files as follows:  
```
	Qasgn11.txt	- Question bank for question 1 of assignment 1
	Qasgn12.txt	- Question bank for question 2 of assignment 1
	Qasgn21.txt	- Question bank for question 1 of assignment 2
	Qasgn22.txt	- Question bank for question 2 of assignment 2
	Qasgn31.txt	- Question bank for question 1 of assignment 3
	Qasgn32.txt	- Question bank for question 2 of assignment 3
	Qtest11.txt	- Question bank for question 1 of test 1
	Qtest12.txt	- Question bank for question 2 of test 1
	Qtest13.txt	- Question bank for question 3 of test 1
	Qtest21.txt	- Question bank for question 1 of test 2
	Qtest22.txt	- Question bank for question 2 of test 2
	Qtest23.txt	- Question bank for question 3 of test 2
	Qsample1.txt	- Sample question 1 for practice
	Qsample2.txt	- Sample question 2 for practice
```  
2.	The contents of the above files are formatted like this:
```
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
number. Total number of questions will be automatically calculated. But
total marks is not (yet).
_                                                         [x marks] 
</QUESTION>
```

* The format makes use of tags similar to HTML but very very sparingly. The only important tags are <QUESTION> and </QUESTIONS> to separate one question from another. Formatting of paragraphs, line breaks, spacing etc are done manually, just like a plain text file.

* These files mentioned above, must reside in /srv/pub/spilt.

### 3.2.	Instructions for Students
1.	Start Ubuntu Linux.

2.	Open a terminal window.

3.	Enter the following command (ignore the $ sign. It’s there just to indicate it is a command prompt):
```
 	$ labtest
```
4.	There should be a prompt for you to enter your student ID. Enter your student ID. The program will look up for your ID and if found will display your name, the number of questions to be answered, and a list of commands that it understands.

* The valid commands are:
```
	v or view      - Display current question
	e or edit      - Start writing a C program to answer the question or to continue editing
                     the current C program. gedit editor will be opened in a new window
                     (if it is not already opened) containing the C program you are writing
                     for the current question. The program file is automatically named
                     according the the question number, i.e. program1.c for question 1,
                     program2.c for question 2 and so forth.
	c or compile   - Compile the C program (created above) using gcc
	r or run       - Run the program (when compilation is successful)
	s or submit    - Submit the answer/program to server. If there are more questions to answer
                     it will increment to the next question number.
	h or help		- Display the help screen which briefly describes 
```
* Note: You need to enter the command by typing its assigned letter followed by the ‘Enter’; or a full command word followed by the ‘Enter’ key.

5.	Press the ‘Enter’ key in order to view the first question. Read the question and start to prepare your answer.

6.	To write your answer, you will need to write a C program using the designated text editor i.e. gedit. Thus, enter e or edit command. Gedit will create a blank C source file for you to start writing your program. The file is not totally empty though. The text of the question will appear in the top comment section of the file. This should help you with answering the question correctly.

7. 	When you are ready, save your program using the save option in gedit. It should be available in its menu. If you prefer, just press Ctrl-S. You then can exit gedit to return to SPILT. Press Ctrl-Q if you prefer the keyboard shortcut.
 
8.	Here, you can compile your program by invoking the c or compile command. SPILT will call gcc to compile your program. Any error message by gcc will appear on your screen after compilation is completed. SPILT will display an appropriate message depending upon whether the compilation was successful or errors have been detected.

9.	If you need to make any corrections, repeat steps 6 (edit) to 8 (compile).

10.	If your program was compiled successfully, you can run it to test its output. This is done by entering the r or run command. 

11.	If you are unsatisfied with your program, repeat steps 5 (edit) to 9 (run).

12.	When you are satisfied with your answer (program) use the s or submit command to submit your program to the server.

13.	After successful submission, you will automatically advance to the next question. Thus you can repeat the above steps again until all the questions in the assessment are answered.


## 4.	Limitations, restrictions, quirks…
1.	Everything is text-based. User interface, question file etc are in plain text. So, cannot include graphics in questions ☹

2.	No checking whether a student has actually answered the first question before he moves on to question number 2. When he submits a file, he is automatically advanced to the next question. Maybe we should put a password that a GA/instructor can key in?

3.	Only one file can be submitted for each question. Breaking this limitation is (should be?) the next thing to do, that is automatically execute the program (partly handle limitation number 2 above), redirect the output to a file (how to handle input if there is any?) and send both files to the server.

4.	Some of the PCs are failing. Only maybe about 20 students can do the lab test at the same time.

5.	If a student is interrupted half-way (eg PC hangs) he can continue on another PC. However the scripts seem to give an error warning by saying that his working directory etc already exist etc. Just ignore the warnings.

6.	The files copied to the server need to be “collected” manually after the test. Looking into each answer/program will be tedious. Badly need a suggestion on this one.

7.	The working directory is left as is after the test. Instructors may want to manually remove the working directory before the next student use the PC.





