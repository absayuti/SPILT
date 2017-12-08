#!/usr/bin/python
#
# The SPILT Shell
#
from __future__ import print_function  # for compatibility
#
version='0.87'    # Rev 4
"""
To do:
    *	FIX problem of using tee to redirect outputs (on hold)
    * 	Add cmd line arg --> -r = pick random question from a list
	                            (for single question assignment)
    * 	status file - + student id, hostname 
    * 	timestamp sync with server? is it possible?
12 Aug 2014
	*	Revision #3 of Version 0.87
	*   Changed banner for "demo" and red colour
	*   To fix time limit display at right side in short_help()
	
11 Aug 2014
	*	Revision #3 of Version 0.87
	*	Fixed wrong year in this section :(
	*	Fixed error with cmd line option --help
	
17 Apr 2014
    *   Bug fixes --- start time, gcc -lm
15 Apr 2014 
	*	Version 0.87
	*	Added PRACTICE mode option.
    *   Added function to scan and store question files in a list
    *	Added 2 minutes extra time and time remaining warning
    
14 Apr 2014 
	*	Version 0.85
    *   Change handling of questions according to sets:
        Each file contains a set of questions Q1, Q2..., Q5
        so that the problems have continuity.
		
21 Aug 2013
    *   Version 0.81
    *   Fixing bugs when run on 2.7
    *   Handle error when question file does not exist   (??)
        (some other fixes as well -- felt like I've done this
        before)
    
12 Apr 2013
    *   Version 0.80
    *   Handle random questions like this:

        Files:  qlabtstN.txt --> contains X question of level N
        Method: Question 1 --> get a random question from qlabtst1.txt
                Question 2 --> get a random question from qlabtst2.txt
                Question 3 --> get a random question from qlabtst3.txt
                and so on...
                Command line argument --> specify how many questions.. up to
                level ...4 or level 5 ... etc. Or may two arguments: from
                level A to B.
        Advantage:
            Can grow the question bank by keeping old questions as well as
            add new ones. Brilliant!!!
            
09 Apr 2013
    * 	Code reformatting
    *   Added more options to simplify user's input: edit, compile, run
    *   Help screen updated
    *   Also allows single letter input: e for edit, c for compile etc
    *   Fixed filename to program1, program2, program3 etc
    *   Submit no longer check for password but check if the program is
        can be compiled successfully
        
11 Mar 2013
    * 	Added time limit info on short help
    * 	Fixed prompt ... used new variables to keep status of time
    * 	... used new varible to track if all question asnwwerd
    * 	When submit, question and answer both piped/copied into 
		answerN.c files
    * 	Convert to python3 compatible
18 feb 2013
    * 	Fixed use of correct question file name for -l (LABTEST)
7 Jan 2013 V 0.64
    * 	Added parameter -n X for selection of single question to be used
		for assignment type of assesment.
    * 	Added parameter -t for test_type. Default = 'assignment'
    * 	Add cmd line arg --> -q = specify file name for questions
    * 	Display title of test/questions
4 Jan 2013 V 0.63
    * 	Used def main() and moved it to top
    * 	Added time limit via argument. Default = 60 minutes.
    * 	Added cmd line argument handling function. To be expanded.
    * 	Added student's name and question no/total question in short 
		help.
    * 	Changed prompt to show lime lapsed instead of current time
1 Jan 2013 V 0.62
    * 	submit
    * 	edit file/programX.c -- partial
    * 	change working dir to ~/spilt.XXXXX
31 Dec 2012
    * 	Added function to create new status file in new format
    * 	Added function to verify student ID
    * 	Status file read correctly for new format, with timestamp
    * 	Removed duplicate functions/lines
17 Dec 2012
    * 	Started with changing view.X.X.sh to spiltXX.py
"""
#-------------------------------------------------------------------------------

import sys, os, time, datetime, glob
import getpass      # to hide password entry
import getopt       # to capture / process cmd line arguments
import random       # for random numbers


#-------------------------------------------------------------------------------
# Important global variables

_debug 	    = False
workdir     = os.path.expanduser('~')	    # base of working dir
spiltdir    = '/server/bin/spilt/'          # SPILT dir on server
studentlist = spiltdir + 'studentlist.txt'
statusfname = 'status.085' 
ref_file    = spiltdir + 'reference.dat'
qfile_asgn  = spiltdir + 'qassign'         	# Part of filename for assignment
qfile_test  = spiltdir + 'qtest'           	# For version 0.85
qtestset    = []							# Full filenames of question files
qsets       = 0         					# Total number of question sets 
qsample     = 'qsample.txt'					# Sample questions for practice
mode       = 'LABTEST'                    	# DEFAULT test type
qfilename   = ''    	                  	# Question filename is set in here
qcurrent    = 0     	# to hold current question number being attempted
qpick       = 0         # Serial number of question-set randomly picked 
qtotal      = 4     	# Total number of questions, default is 4
studentid   = -1    	# student id is to be read from file
studentname = ''    	# student name is to be read from file
duration    = 60    	# Default duration for a test session is 60 minutes but can be
						# changed through cmd line argument -t xx
all_done    = False     # set if all question is done
time_over	= False		# Set if time is over the limit

################################################################################
# Main function starts here
################################################################################

def main(argv):
    
	process_arguments(sys.argv[1:])
	disp_header()
	if mode=='PRACTICE':
		init_practice()
	else:
		initialize()
	
	while True:

		command = prompt()						# process command entered
		if command=='exit' or command=='x':
			ask_exit()
		elif command=='':
			beep()
		elif command=='help' or command=='h':
			disp_header()
			disp_help()
			disp_short_help()
		elif command=='view' or command=='v':
			print()
			if _debug: print(qfilename)
			disp_question(qfilename, qcurrent)
			disp_short_help()
		elif command=='edit' or command=='e':
			edit_program()
			disp_short_help()
		elif command=='compile' or command=='c':
			if compile_program(qcurrent)==0:
				print(' Enter '+txtund+'r'+txtrst+'un to execute/run the program.\n')
			disp_short_help()
		elif command=='run' or command=='r':
			disp_header()
			run_program()
			disp_short_help()
		elif command=='submit' or command=='s':
			disp_header()
			if confirm_submit():
				if submit_answer(qcurrent)==0:
					next_question()
					if mode!='PRACTICE':
						update_status_file()
					if not all_done:
						disp_question(qfilename, qcurrent)
						disp_short_help()
					else:
						cleanup_exit()
				else:
					disp_short_help()
		else:
			os_command(command)


#-------------------------------------------------------------------------------

def process_arguments(argv):

    global mode, qfilename, qfile_test, qfile_asgn
    
    try:
        opts, args = getopt.getopt(argv, "hpt:q:n:", ["help","debug"])
    except getopt.GetoptError:
        disp_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            disp_usage()
            sys.exit()
        elif opt == "--debug":
            global _debug
            _debug = True
        elif opt == "-p":
            mode = 'PRACTICE'
            duration = 10
        elif opt in ("-t"):
            global duration
            duration = int(arg)
        elif opt in ("-q"):
	        #global questfile
            qfilename = spiltdir + arg
            for n in range(1,5):
				disp_question( qfilename, n)
				print()
            sys.exit()
        elif opt in ("-n"):
            global single_question
            single_question = int(arg)
            print("Do question", single_question, "only.")
    return


#------------------------------------------------------------------------------

def disp_usage():

    print("\nUSAGE... options:")
    print(" -h, --help  = help (this text)")
    print(" -p          = set practice mode")
    print(" -q xxxxxxx  = load question file xxxxxxx")
    print(" -n x        = do question x only")
    print(" -t xx       = specify maximum duration (time) = xx minutes")
    print();
    ##print(" --d          = debug mode")


#==============================================================================

def init_practice():
	"""
	Get/verify user ID, initialise global variables, create working
	directory, display help, set time limit
	"""
	global workdir, xfrdir, statusfile, studentid, studentname
	global qfilename, qcurrent, qtotal, qpick, mode
	global time_start, time_limit, time_extra

	xfrdir  = workdir + '/prac.tmp/'
	workdir = workdir + '/prac.tmp/'				# set practice directory
	try:
		os.chdir(workdir)			    			# Try to move to working dir
	except:
		print(' Creating local working directory')
		retval = os.system('mkdir ' + workdir)      # Create one if it does not exist
		os.chdir(workdir)			    			# Try again to move to working dir

	qfilename = spiltdir + qsample
	qtotal = 2
	next_question()
	disp_help()
	wait_enter()
	time_start = datetime.datetime.now()

	# check if question file exist
	if not os.path.isfile(qfilename):
		print( txtemp+' Error: Unable to find question file. Program terminated.\n'+txtrst)
		sys.exit()
    
	if _debug: print('Initialise', qcurrent, qpick)

	disp_question(qfilename, qcurrent)               		# display current question
	time_limit = time_start + datetime.timedelta(0,300)		# five min for practice
	time_extra = time_limit
	disp_short_help()


#-------------------------------------------------------------------------------

def initialize():
	"""
	Get/verify user ID, initialise global variables, create working
	directory, display help, set time limit
	"""
	global workdir, xfrdir, statusfile, studentid, studentname
	global qfilename, qcurrent, qtotal, qpick
	global time_start, time_limit, time_extra

	random.seed()
	disp_header()
                                            
	verify_student_id()
	xfrdir = '/xfr.srv/spilt.' + str(studentid)+'/' # transfer/status dir
	workdir = workdir +'/spilt.'+str(studentid)+'/' # set student's working directory
	try:
		os.chdir(workdir)			    			# Try to move to working dir
	except:
		print(' Creating local working directory')
		retval = os.system('mkdir ' + workdir)      # Create one if it does not exist
		os.chdir(workdir)			    			# Try again to move to working dir

	get_qfile_sets()								# Get list of Q files
	
	statusfile = xfrdir + statusfname               # check/create status file
	if _debug: print('status file: ', statusfile)
	if os.path.isfile(statusfile):                  # check if student already started before
		time_start = read_status_file()             
		print(' Started at:', time_start, '\n')
		qfilename = qtestset[qpick]					# Get the file name
	else:
		qpick = random.randint(0, qsets-1)			# Pick set # 0 ~ 4
		qfilename = qtestset[qpick]					# Get the file name
		next_question()
		disp_help()
		wait_enter()
		time_start = datetime.datetime.now()
		create_status_file()                

	# check if question file exist
	if not os.path.isfile(qfilename):
		print( txtemp+' Error: Unable to find question file. Program terminated.\n'+txtrst)
		sys.exit()
    
	if _debug: print('Initialise', qcurrent, qpick)

	disp_question(qfilename, qcurrent)               # display current question
	time_limit = time_start + datetime.timedelta(0,duration*60)
	time_extra = time_start + datetime.timedelta(0,(duration+2)*60)
	disp_short_help()


#-------------------------------------------------------------------------------
# Search and find questions files

def get_qfile_sets():

	global qfiles, qsets
	for name in glob.glob( spiltdir + 'qtest*.txt'):
		qtestset.append( name )
	qsets = len( qtestset )


#-------------------------------------------------------------------------------
# function to diplay prompt and get command from user

def prompt():

	global time_over

	now = datetime.datetime.now()
	lapsed = now - time_start
	if now < time_limit:
		print(' '+txtbld+str(lapsed)[0:7]+' Option or Command ===> '+txtrst, end='')
		try:
			entry = raw_input()   # for python 2.x
		except:
			entry = input()
	else:
		time_over = True
		if now < time_extra:
			remain = time_extra - now	
			print( txtemp + ' Time is up, please submit your answer. Session will end in less than ' 
						  + str(remain.seconds) + ' sec.' + txtrst )
			print( bakred+' '+str(remain.seconds)+'s ===> '+txtrst, end='' )
			try:
				entry = raw_input()    # for python 2.x
			except:
				entry = input()
		else:
			print( txtemp + '\n\n Sorry, your time is up. Session has ended.'+ txtrst) 
			cleanup_exit()
	
	return entry.strip()


#-------------------------------------------------------------------------------
# Wait for user to press ENTER 

def wait_enter():
	
    print('\n Press '+txtbld+'[Enter]'+txtrst+' to continue ', end='')
    try:
        entry = raw_input()   # for python 2.x
    except:
        entry = input()


#-------------------------------------------------------------------------------
# Just sound a beep

def beep():
    print( '\a'+crsrup )


#-------------------------------------------------------------------------------
# open file with supplied name and mode

def open_file(filename, opmode):
    """Open a file, check for error"""
    if _debug: print('Opening', filename, opmode)
    try:
        the_file = open(filename, opmode)
    except(IOError) as e:
        print(txtemp+" ERROR: Unable to open the file", filename, "\n Ending program.\n"+txtrst, e )
        input("\n\n Press [Enter] to exit.")
        sys.exit()
    else:
        return the_file


#-------------------------------------------------------------------------------

def verify_student_id():
    global studentid, studentname
    print("")
    #student = raw_input(" Please enter your student ID: ")
    student = input(" Please enter your student ID: ")
    student = int(student)
    student_found = False
    count = 0
    print(" Verifying Student ID", student)
    f = open_file(studentlist, 'r')
    line = f.readline()
    while line:
        word = line.split()
        st_id = int(word[0])            # first word is the ID
        st_name = ' '.join(word[1:])    # the rest contain the name
        count = count + 1
        ###print( count, st_id, st_name )
        if st_id == student:
            student_found = True
            studentid = st_id
            studentname = st_name
            break
        line = f.readline()
    f.close()
    if student_found:
        print()
        print( txtbld, "Welcome", studentname, txtrst )
        print()
        time.sleep(3)
    else:
        print()
        print( txtemp+" ERROR: Could not find student ID", student, txtrst )
        print()
        print(" (Total list scanned: ",count,")")
        print()
        sys.exit()


#-------------------------------------------------------------------------------

def create_status_file():
    """
    Create new status file
    Status file format (v0.85):

	#   nnnnnn  student name
	1   x   4    yy/mm/dd    hh:mm:ss   <-- start time
	2   x   4    yy/mm/dd    hh:mm:ss
   	3	x   4    yy/mm/dd    hh:mm:ss
	4   x   4    yy/mm/dd    hh:mm:ss
	0   0   0    yy/mm/dd    hh:mm:ss   <-- 0 0 0 = done!
	^   ^   ^
	|   |   '-------- total Q to answer
	|   '---------- qpick = random file ### from the set
	'--------- Q # completed
    """
    print(" Creating new status file...")
    cmdline = "mkdir " + workdir
    retval = os.system(cmdline)
    cmdline = "cd " + workdir
    retval = os.system(cmdline)
    cmdline = "mkdir " + xfrdir
    retval = os.system(cmdline)
    f = open_file(statusfile, 'w')
    timestamp = datetime.datetime.now()
    f.write('# %s  %s\n' %(str(studentid), studentname))
    f.write('%d  %d  %d  %s\n' %(qcurrent, qpick, qtotal, timestamp))
    f.close()


#-------------------------------------------------------------------------------

def read_status_file():
	"""
	Read the status of the student
	This file contain: quest_no, total_question, date, time
	"""
	global qcurrent, qpick, qtotal

	print(" Reading status file...")
	f = open_file(statusfile, 'r')
	line = f.readline()
	count = 0
	while line:
		words = line.split()
		if count==1:				# if first line of data, get date & time
			q_date = words[3]
			q_time = words[4]
		if _debug: print( words )
		line = f.readline()         # we are only interested in the last 
		count = count+1
	f.close()
	q_no = words[0]                 # current q#
	q_pick = words[1]
	q_max = words[2]                # last q#
	#q_date = words[3]
	#q_time = words[4]

	t = q_date + " " + q_time
	t = time.strptime(t[:19], '%Y-%m-%d %H:%M:%S')
	if _debug: print( t )
	st_time = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
	#raw_input(st_time)

	if int(q_no) == 0:
		print( txthlt + "\n No more question to answer. You are done.\n"+txtrst )
		sys.exit()
	else:
		qcurrent = int(q_no)
		qpick = int(q_pick)
		qtotal = int(q_max)
		print(" Current question number:", qcurrent, "out of", qtotal )
	return st_time


#-------------------------------------------------------------------------------
    
def update_status_file():
            
    f = open_file(statusfile, 'a')
    timestamp = datetime.datetime.now()
    f.write("%d  %d  %d  %s\n" % (qcurrent, qpick, qtotal, timestamp))
    f.close()


# -------------------------------------------------------------------------------

def next_question():

	global qcurrent, qpick, qtotal, all_done, qfilename

	if qcurrent < qtotal:
		qcurrent = qcurrent + 1
		print(" Current question number: ", qcurrent, "(out of ", qtotal, " questions)")
        
		if _debug:
			print('next_question():', qfilename, qcurrent)
	else:
		qcurrent = 0
		qpick = 0
		qtotal = 0
		disp_header()
		print( '\n\n'+ txthlt + " Congratulations! You're done!\n" + txtrst)
		all_done = True
	print()


#-----------------------------------------------------------------------

def disp_question(filename, questno):

    if _debug: print('disp_question', filename, questno)
    f = open_file(filename, 'r')
    disp_header()

    marker  = '<QUESTION' + str(questno).strip() + '>'
    markend = '</QUESTION>'
    state   = 'search' 
    while True:
        line = f.readline()
        if state == 'search':
			if line.strip() == marker:
				#print( bldcyn+"[Question: "+str(qcurrent)+"]"+txtrst )
				print( bldcyn+"[Question: "+str(questno)+"]"+txtrst )
				print()
				state = 'found'
			else:
				continue
        elif state == 'found':
            if line.strip() == markend:
                print()
                #print( bldcyn+"[End of Question "+str(qcurrent)+" of "+str(qtotal)+"]"+txtrst )
                print( bldcyn+"[End of Question "+str(questno)+" of "+str(qtotal)+"]"+txtrst )
                f.close()
                return
            else:
                line = line.replace('<em>', txtemp)
                line = line.replace('</em>', txtrst)
                line = line.replace('<b>', txtbld)
                line = line.replace('</b>', txtrst)
                line = line.replace('<u>', txtund)
                line = line.replace('</u>', txtrst)
                line = line.replace('<code>', txtcod)
                line = line.replace('</code>', txtrst)
                print( line, end='' )
    f.close()
    # No question found
    print()
    print( txtemp+" ERROR: Question no.", questno, "not available." )
    print( " ...... Ending program."+txtrst )
    input("\n\n Press [Enter] to exit.")
    sys.exit()


#-------------------------------------------------------------------------------

def get_qcount(filename):
    f = open_file(filename, 'r')
    qcount = 0
    line = f.readline()
    while line:
        if line.strip() == "<QUESTION>":
            qcount = qcount+1
        line = f.readline()
    f.close()
    return qcount


#-------------------------------------------------------------------------------

def disp_header():

    os.system("clear")
    if mode=='PRACTICE':
        print( bakred+bldwht+" =SPI-LT=================================================================="+version+"=")
        print(" =                                                                            =")
        print(" =                        D E M O / Practice Session                          =")
        print(" =                                                                            =")
        print(" ==============================================================================")
        print( crsrup+" ========================================================================("+str(qcurrent)+"/"+str(qtotal)+")"+txtrst)
    else:
        print( bakblu+bldwht+" =SPI-LT=================================================================="+version+"=")
        print(" =                       UNIVERSITI TEKNOLOGI PETRONAS                        =")
        print(" =            Department of Electrical and Electronic Engineering             =")
        print(" =              EDB1023 Structured Programming and Interfacing                =")
        print(" =============================================================================="+txtrst)
        print( crsrup+bakblu+bldwht+" ========================================================================("+str(qcurrent)+"/"+str(qtotal)+")")
        print( crsrup+' ='+studentname+txtrst )
    

#-------------------------------------------------------------------------------

def disp_help():

	disp_header()
	print()
	print('                        ' +txthlt+' P R A C T I C A L   T E S T '+txtrst)
	print()
	print(' o Questions must be answered in order')
	print()
	print("   - Enter "+txtund+"view"+txtrst+" to view current question ("+ str(qcurrent) +" out of "+ str(qtotal) +")")
	print("   - Enter "+txtund+"edit"+txtrst+" to edit your program/answer.")
	print("   - Enter "+txtund+"compile"+txtrst+" to compile your program using "+txtbld+"gcc"+txtrst)
	print("   - Enter "+txtund+"run"+txtrst+" to "+txtbld+"execute"+txtrst+" your program.")
	print("     Verify that the program and its output answers the question correctly.")
	print()
	print(" o Repeat any of the above steps until you are satisfied with your work")
	print()
	print(" o Enter "+txtund+"submit"+txtrst+" to submit your answer (source code) and move on to the next")
	print("   question.")
	print()
	print(txtemp +"   CAUTION: Once an answer is submitted, the question CAN'T be viewed anymore"+txtrst)


#-------------------------------------------------------------------------------

def disp_short_help():
    print("___________________________________________________________________________(" +
    		str(duration)+")")
    print(" Options:   " +txtund+"h"+txtrst+"elp  " +txtund+"v"+txtrst+"iew  " +
    		txtund+"e"+txtrst+"dit  " +txtund+"c"+txtrst+"ompile  " +
    		txtund+"r"+txtrst+"un  " +txtund+"s"+txtrst+"ubmit  " +
    		"e"+txtund+"x"+txtrst+"it   ")


#-------------------------------------------------------------------------------

def edit_program():

    progname = 'program'+str(qcurrent).strip()+'.c'
    fname = workdir+progname
    if _debug: print('Afile', fname, '#', qcurrent)

    if not os.path.isfile(fname):                 # If file does not exist, create new
    	create_new_program( fname )

    if os.path.isfile(fname):                  # If file succesfully created or already exist, open it
        print(' Opeaning program file in a new window...')
        os.system('gedit ' + fname + ' + &')
        print(' Program file '+progname+' opened for editing in another window.')


#-------------------------------------------------------------------------------

def create_new_program( fname ):

	print(' Creating file', fname)
	fo = open_file(fname, 'w')
	fo.write('/*****************************************************************************\n')
	fo.write(' * '+ str(studentid) +' '+ studentname +'\n')
	fo.write(' * '+ fname +'\n')
	fo.write(' *\n')                                                       
	fi = open_file(qfilename, 'r')              # copy question as comment's content into file
	if _debug: print('Qfile', qfilename, '#', qcurrent)
	
	marker  = '<QUESTION' + str(qcurrent).strip() + '>'
	markend = '</QUESTION>'
	state   = 'search' 

	while state != 'done':
		line = fi.readline()
		if _debug: print(line)
		if state == 'search':
			if line.strip() == marker:
				fo.write(" * Question "+str(qcurrent)+'\n')
				state = 'found'
			else:
				continue
		elif state == 'found':
			if line.strip() == markend:
				state = 'done'
				break
			else:
				line = line.replace('<em>','')
				line = line.replace('</em>','')
				line = line.replace('<b>','')
				line = line.replace('</b>','')
				line = line.replace('<u>','')
				line = line.replace('</u>','')
				line = line.replace('<code>','')
				line = line.replace('</code>','')
				fo.write(' * '+line)
	
	fi.close()
	fo.write(' * This portion is automatically generated when you chose the EDIT option.\n')
	fo.write(' ******************************************************************************/\n\n')
	fo.write('#include <stdio.h>\n\n')
	fo.close()



#-------------------------------------------------------------------------------

def compile_program(questno):
    progfile = 'program'+str(questno).strip()+'.c'
    fname = workdir+progfile
    print('\n Compiling '+progfile+'...\n')
    cmdline = 'gcc -Wall '+fname + ' -lm'
    retval = os.system(cmdline)
    if retval==0:
        print(' OK.\n')
    else:
        print(txtemp+'\n Please check your program.\n'+txtrst)
    return retval


#-------------------------------------------------------------------------------

def run_program():
    print(' --------------------========= Executing Program =========--------------------')
    os.system('./a.out')
    print(' --------------------===== End of Program Execution ======--------------------')


#-------------------------------------------------------------------------------

def submit_answer(questno):
                                                    # Compile program before submitting
    if compile_program(questno)==0:
        progfile = 'program'+str(questno).strip()+'.c'
        fname = workdir+progfile
        print( txtbld+" Submitting", fname, "to server..."+txtrst)
        xfrfilename = xfrdir+'answer'+str(questno)+'.c'
        if os.path.isfile(xfrfilename):             # if file already exist, add numbered extension
            print(" File with same name already exist. Renaming...")
            count = 1
            bckfilename = xfrfilename+'.'+str(count).strip()
            while os.path.isfile(bckfilename):
                count = count + 1
                bckfilename = xfrfilename+'.'+str(count).strip()
            xfrfilename = bckfilename                   # dest file take highest numbered extension                                                       
        os.system('cp '+ fname +'  '+ xfrfilename)      # copy program source code
        print( txtbld+" OK."+txtrst)
        wait_enter()
        return 0
    else:
        print( txtemp+' Compilation error. Answer is NOT submitted.\n'+txtrst)
        print( txtemp+' Please check your program and try again.\n'+txtrst)
        return -1


#-------------------------------------------------------------------------------

def get_prog_filename():
    """
    Get the file name of user's program (answer) and verify if it exist.
    """
    # List *.c files in current directory
    print('\n Listing C programs in current directory:\n')
    retval = os.system('ls *.c')
    if retval != 0:
        print('\n No C programs found in current directory.')
        print(' Please specify full path when entering your file name below.')

    file_exist = False
    while not file_exist:
        print("\n Please enter your program's file name (leave it blank to cancel)")
        try:
            filename = raw_input(" File name = ")
        except:
            filename = input(" File name = ")
        if filename=="":
            return
        if os.path.isfile(filename):
            print(" File", filename, "found.")
            file_exist = True
        else:
            print()
            print( txtemp+" ERROR: File ", filename, "could not be found.")
            print(" Please try again."+txtrst )
    return filename

    
#-------------------------------------------------------------------------------
# submit output ------not used at the moment 
#                     To work on it later....
# 
def record_output(progname):
    # check again if file exist?
    if os.path.isfile(progname):
        print("\n Attempting to compile ", progname, "...\n")
        cmdline = "gcc -lm -Wall "+progname
        retval = os.system( cmdline )
        if retval==0:
            print("OK\n Now attempting to execute and record the output of the program...\n")
            print("************************* program", progname, "start *************************\n")
            cmdline = "./a.out | tee output.txt"
            retval = os.system( cmdline )
            print("************************* program", progname, "end *************************\n")
            if retval==0:
                print("OK.\n")
                return 0
            else:
                print("\n Error occured when executing ", progname, "\n")
                return -1
        else:
            print("\n Error occured when compiling ", progname, "\n")
            return -2
    else:
        print("\n I really don't know what's wrong but can't find", progname);
        print("\nBummer!\n");
        return -9
    

#-------------------------------------------------------------------------------
    
def read_ref_file(questno):
    """ Read the list of things """
    f = open_file(ref_file,'r')
    i = 0
    word = "-"
    while word:
        if i==questno:
            ##print( word, i, questno )
            break
        else:
            word = f.readline().strip()
            i = i + 1
    f.close()
    return word


#-------------------------------------------------------------------------------

def confirm_submit():

	if _debug:
		print('SUBMIT', qfilename, qcurrent)

	print( txtbld+"\n You chose to submit your answer.\n Are you sure?"+txtrst)
	print(" Please enter "+txtbld+"y"+txtrst+" or "+txtbld+"n"+txtrst+" >> ", end='')
	try:
	    reply = raw_input()
	except:
	    reply = input()
	if reply=='y' or reply=='Y':
	    return True
	else:
	    return False


#-------------------------------------------------------------------------------
# Chech password --> not used anymore?

def rot13_char(ch):
    if not ch.isalpha():
        return ch
    ch_low = ch.lower()
    if ch_low <= 'm':
        dist = 13
    else:
        dist = -13
    return chr(ord(ch) + dist)
#
#
def rot13(s):
    return ''.join( rot13_char(ch) for ch in s )
#
#
def verify_password():
    pw = getpass.getpass(txtbld+" Lecturer/Instructor"+txtrst+", please enter password: ")
    ##print( rot13(pw), read_ref_file(int(questno)), questno)
    if rot13(pw)==read_ref_file(int(questno)):
        print( txtbld+" Password verified."+txtrst)
        return True
    else:
        print( txtemp+" Sorry. Please try again."+txtrst)
        return False


#-------------------------------------------------------------------------------

def ask_exit():

	print( txtemp+"\n You chose to exit.\n"+txtrst)
	print(" All the files created during this session will be deleted.")
	print(" Are you sure you want to exit this program?")
	try:
		reply = raw_input(" Please enter "+txtemp+"y"+txtrst+" or "+txtemp+"n"+txtrst+" >> ")
	except:
		reply = input(" Please enter "+txtemp+"y"+txtrst+" or "+txtemp+"n"+txtrst+" >> ", end='')
	if reply=='y' or reply=='Y':
		cleanup_exit()


#-------------------------------------------------------------------------------
        
def cleanup_exit():
        
	print( txtbld+"\n Removing temporary files..."+txtrst )
	os.system("cd ~")
	cmdline = "rm -r "+workdir
	if _debug: print( cmdline )
	os.system( cmdline )
	#os.system("clear")
	print( txtbld+"\n Thank You.\n"+txtrst )
	sys.exit()


#-------------------------------------------------------------------------------

def os_command(line):
    print( txtbld+" Passing the command to the OS..."+txtrst )
    retval = os.system(line)
    print( txtbld+" Return value =", retval, txtrst )
    disp_short_help()


#-------------------------------------------------------------------------------
# Escape codes for colours 

txtblk='\033[0;30m' # Black - Regular
txtred='\033[0;31m' # Red
txtgrn='\033[0;32m' # Green
txtylw='\033[0;33m' # Yellow
txtblu='\033[0;34m' # Blue
txtpur='\033[0;35m' # Purple
txtcyn='\033[0;36m' # Cyan
txtwht='\033[0;37m' # White
bldblk='\033[1;30m' # Black - Bold
bldred='\033[1;31m' # Red
bldgrn='\033[1;32m' # Green
bldylw='\033[1;33m' # Yellow
bldblu='\033[1;34m' # Blue
bldpur='\033[1;35m' # Purple
bldcyn='\033[1;36m' # Cyan
bldwht='\033[1;37m' # White
undblk='\033[4;30m' # Black - Underline
undred='\033[4;31m' # Red
undgrn='\033[4;32m' # Green
undylw='\033[4;33m' # Yellow
undblu='\033[4;34m' # Blue
undpur='\033[4;35m' # Purple
undcyn='\033[4;36m' # Cyan
undwht='\033[4;37m' # White
bakblk='\033[40m'   # Black - Background
bakred='\033[41m'   # Red
bakgrn='\033[42m'   # Green
bakylw='\033[43m'   # Yellow
bakblu='\033[44m'   # Blue
bakpur='\033[45m'   # Purple
bakcyn='\033[46m'   # Cyan
bakwht='\033[47m'   # White
txtrst='\033[0m'    # Text Reset
crsrup='\033[1A'    # Cursor up

txtbld=bldgrn
txtemp=bldred
txtund=undylw
txtcod=txtgrn
txthlt=bakgrn+bldwht
              

#-------------------------------------------------------------------------------
# Call main() 

if __name__ == "__main__":
   main(sys.argv[1:])

# End of program
#-------------------------------------------------------------------------------

