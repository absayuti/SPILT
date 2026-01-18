#!/usr/bin/python
#
# (S)tructured (P)rogramming and (I)nterfacing (L)ab (T)est
#
# Requires:  Python 2.7 or Python 3.x  (Supposed to be compatible with 2.7 & 3.x) 
# Author: AB Sayuti HM Saman
#
# Requires the file:  spilt.config  (in the same directory as this program)
#
# Please read the README file.... somewhere in the same directory as this file
# 
# ========================================================================================

from __future__ import print_function          # for compatibility

import sys, os, select, time, datetime, glob
#import getpass                              # to hide password entry
import getopt                               # to capture / process cmd line arguments
import random                               # for random numbers
import socket                                  # Import socket module

version        = '0.09.400'                 # Ixelles Rev 34.0 ???
                                            # 22 Dec 2025
                                            # Installing in new set of Server and PC running Ubuntu 24
                                            # Apparently socket.error() exception has new format now.
                                            # Possibly other exceptions too. I have not been using Python 3
                                            # or Pythons in general for quite a while (4 years?).

# ========================================================================================
# Important global CONSTANTS/variables

SERVERNAME  = '172.17.9.41'                # Server IP used by socket objects
#old entry: SERVERNAME  = '172.17.101.201'                # Server IP used by socket objects
HOSTNAME    = socket.gethostname()
SPILTDIR    = '/mnt/pub/spilt/'             # SPILT dir on server
CONFIGFILE    = SPILTDIR+'spilt.config'
SRVXFR      = '/mnt/xfr/spilt/'                # Base of transfer dir on server
HOMEDIR     = os.path.expanduser('~')+'/'    # User home dir
TEMPDIR        = HOMEDIR+'.temp/'

S_workdir   = { 'asgn1':TEMPDIR+'a1/', 'asgn2':TEMPDIR+'a2/', 'asgn3':TEMPDIR+'a3/',
                'labtest1':TEMPDIR+'t1/', 'labtest2':TEMPDIR+'t2/', 
                'practice':TEMPDIR }
                
S_xfrdir    = { 'asgn1':SRVXFR+'a1/', 'asgn2':SRVXFR+'a2/', 'asgn3':SRVXFR+'a3/', 
                'labtest1':SRVXFR+'t1/', 'labtest2':SRVXFR+'t2/', 
                'practice':TEMPDIR }

# Prefix for Q files, including the path/dir
S_filepref  = { 'asgn1':SPILTDIR + 'Qasgn1', 'asgn2':SPILTDIR + 'Qasgn2', 'asgn3':SPILTDIR + 'Qasgn3', 
                'labtest1':SPILTDIR + 'Qtest1', 'labtest2':SPILTDIR + 'Qtest2', 
                'practice':SPILTDIR + 'Qsample' }
S_questions = {}
S_duration  = {}

with open( CONFIGFILE,"r") as f:
    for line in f:
        if line[0] != '#' and line[0] != '\n':
            key, ques, dur = line.split()
            S_questions[key] = int(ques)
            S_duration[key]  = int(dur)
            
qfileset    = []                            # Full filenames of question files 
qsets       = 0                             # Total number of question sets 
qfilename   = ''                            # Qbank filename is set in here
qbuffer     = []                            # Used to temporarily store current question text
qbankbuffer = []                            # Used to temporarily store Qbank contents
qcurrent    = 0                             # Current Q # being attempted
qpick       = 0                             # Index of question picked from set
qtotal      = 0                             # Total number of Qs to answer
statusfname = 'status.090'                  # Status filename for each student
studentlist = SPILTDIR + 'studentlist.txt'
studentid   = 0                             # student id is to be read from file
studentname = 'Practice Session'            # student name is to be read from file
mode        = 'PRACTICE'                    # DEFAULT assessment type
tmode       = 'practice'
duration    = 0                             # Duration for a session can be
                                            # be changed via cmd arg -t xx
all_done    = False                         # set if all question is done
time_over   = False                         # Set if time is over the limit
_debug      = False                         # Are we in debug mode?


# ========================================================================================
# Main function starts here
#
def main(argv):
    
    global duration
    
    process_arguments(sys.argv[1:])
    disp_header()

    if tmode=='view_all':
        view_all_questions( qfilename )
        sys.exit(0)
    else:
        initialize()

    ### Main loop -----------------------------------------------------
    
    while True:

        command = prompt()                    # process command entered
        if command=='exit' or command=='x':
            ask_exit()
        elif command=='':
            print(crsrup)
        elif command=='help' or command=='h':
            disp_header()
            disp_help()
            disp_short_help()
        elif command=='view' or command=='v':
            print()
            if _debug: print('DISPLAY: '+qfilename + str(qpick))
            disp_question_buffer()
            disp_short_help()
        elif command=='edit' or command=='e':
            disp_header()
            edit_program()
            disp_short_help()
        elif command=='compile' or command=='c':
            disp_header()
            if( not compile_program( qcurrent ) ):
                print(' Enter '+txtund+'r'+txtrst+'un to execute/run the program.\n')
            disp_short_help()
        elif command=='run' or command=='r':
            disp_header()
            run_program()
            disp_short_help()
        elif command=='submit' or command=='s':
            disp_header()
            if confirm_submit( qcurrent ):
                if submit_answer( qcurrent )==0:
                    next_question()
                    if tmode!='practice':
                        update_status_file()
                    if not all_done:
                        if _debug: print('DISPLAY: '+qfilename + str(qpick))
                        disp_question_buffer()
                        #disp_short_help()
                    else:
                        cleanup_exit()
                #else:
            disp_short_help()
        else:
            os_command(command)


# ========================================================================================
#  Compute command line arguments
#
def process_arguments(argv):

    global tmode, mode, duration, qfilename
    
    try:
        opts, args = getopt.getopt(argv, "hd:v:q:", ["help","a1", "a2", "a3", "t1", "t2", "debug"])
    except getopt.GetoptError:
        disp_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            disp_usage()
            sys.exit()
        elif opt in ("-d"):
            duration = int(arg)
        elif opt in ("-v"):
            qfilename = SPILTDIR + arg
            print(qfilename)
            mode = 'VIEW_ALL'
            tmode = 'view_all'
        elif opt in ("-q"):
            global single_question
            single_question = int(arg)
            print("Do question "+single_question+" only.")
        elif opt in ("--a1"):
              mode = 'ASSIGNMENT1'
              tmode = 'asgn1'
        elif opt in ("--a2"):
            mode = 'ASSIGNMENT2'
            tmode = 'asgn2'
        elif opt in ("--a3"):
            mode = 'ASSIGNMENT3'
            tmode = 'asgn3'            
        elif opt in ("--t1"):
            mode = 'LABTEST1'
            tmode = 'labtest1'
        elif opt in ("--t2"):
            mode = 'LABTEST2'
            tmode = 'labtest2'
        elif opt in ("--debug"):
            global _debug
            _debug = True

    return


# ========================================================================================
#  Display command line options
#
def disp_usage():

    print_msg("USAGE... options:")
    print(" -h, --help  = help (this text)")
    print(" -v xxxxxxx  = view all questions in file xxxxxxx")
    print(" -q x        = do question x only")
    print(" -d xx       = specify maximum duration (time) = xx minutes")
    print(" --a1        = set mode as assignment #1")
    print(" --a2        = set mode as assignment #2")
    print(" --a3        = set mode as assignment #3")
    print(" --t1        = set mode as lab test #1")
    print(" --t2        = set mode as lab test #2")
    print(" --debug     = run in debug mode")
    return

# ========================================================================================
#  Get/verify user ID, initialise global variables, create working directory, 
#  display help, set time limit, etc for assigment mode
#
def initialize():

    global workdir, xfrdir, statusfile, studentid, studentname
    global qfilename, qcurrent, qtotal, qpick
    global duration, time_start, time_limit, time_extra

    random.seed( time.time()+studentid )
    disp_header()
    
    # Set duration, directories and status file
    if tmode != 'practice': verify_student_id()
    duration = S_duration[tmode]
    xfrdir   = S_xfrdir[tmode]+'.'+str(studentid)+'/'
    workdir  = S_workdir[tmode]+'.'+str(studentid)+'/'
    
    # Move to working directory
    try:
        os.chdir(workdir)
    except:
        print(' Creating local working directory')
        os.system('mkdir ' + TEMPDIR)              # Create one if it does not exist
        os.system('mkdir ' + S_workdir[tmode])
        os.system('mkdir ' + workdir)
        os.chdir(workdir)                        # Try again to move to working dir

    # Check/create/read status file
    statusfile = xfrdir + statusfname               
    if os.path.isfile(statusfile):              # check if student already started before
        time_start = read_status_file_090()     # Get start time, qcurrent, qpick & qtotal
        print(' Started at: '+str(time_start))
        if _debug: print('Status: '+str(qpick)+'/'+str(qtotal))
        qtotal = get_qfileset()                    # Total Qs = number of Qbank files in the series
        qfilename = qfileset[qcurrent-1]        # Set the file name based on current Q#
        load_question_buffer( qfilename, qpick )        # Put question text in qbuffer
        #get_qbank_data( qfilename )                # Buffer the contents of the Qbank file    <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    else:
        qtotal = get_qfileset()                    # Total Qs = number of Qbank files in the series
        qcurrent = 1                            # Start new session with Q #1
        qfilename = qfileset[qcurrent-1]        # Set the file name to target Qbank file
        #get_qbank_data( qfilename )                # Buffer the contents of the Qbank file    <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        n = get_qcount_from_file(qfilename)        # Find out how many Qs in the Qbank file
        qpick = random.randint(1,n)                # Pick single Q position from the Qbank
        load_question_buffer( qfilename, qpick )        # Put question text in qbuffer
        disp_help()                                # Display help if new session
        wait_enter()                            
        time_start = datetime.datetime.now()    # Start timer when user pressed enter
        create_status_file_090()                

    if _debug: print('status file: ', statusfile)

    # Verify that question file exist
    if not os.path.isfile(qfilename):
        print_err(' Error: Unable to find question file. Program terminated.\n')
        if _debug: print( qfilename )
        sys.exit()
    
    time_limit = time_start + datetime.timedelta(0,duration*60)
    time_extra = time_start + datetime.timedelta(0,(duration+2)*60)
    
    now = datetime.datetime.now()
    rt = check_time_over( now )
    if rt != 'TIME_OVER':
        if _debug: print('Display II: '+qfilename + str(qpick))
        disp_question_buffer()                    # display current question
        disp_short_help()
    else:
        print_msg(' Sorry, your time is up. Session has ended. ')
        cleanup_exit()    
    
    if _debug:
        print('Initialise', qcurrent, qpick)
        print('Start = ' + str(time_start) )
        print('Limit = ' + str(time_limit) )
        print('Extra = ' + str(time_extra) )

    return
    

# ========================================================================================
#  Verify that the student ID is in the list
#   Old function was slow because the data is read line by line while
#   being compared with the ID entered. Only apparent when many clients
#   were accessing the same file.
#   Function modified so that the file content is read into a list (array), 
#   then the comparison is done.
#
def verify_student_id():

    global studentid, studentname
    
    student = ''
    while student == '':
        print()
        print(txtbld+" Please enter your student ID: "+txtrst, end='')
        try:
            student = raw_input()
        except:
            student = input()
    print(" Verifying Student ID "+ student)
    
    # Read all data in student list
    f = open_file(studentlist, 'r')
    lines = []
    line = f.readline()
    while line:
        print(".",end='')
        lines.append( line )
        line = f.readline()
    f.close()
    print()

    # Find ID in the lines[] list 
    student_found = False
    count = 0
    for i in range( len(lines) ):
        word = lines[i].split()
        st_id = int(word[0])            # first word is the ID
        st_name = ' '.join(word[1:])    # the rest contain the name
        count = count + 1
        if st_id == int(student):
            student_found = True
            studentid = st_id
            studentname = st_name
            break

    # Tell user whether ID is found in list
    if student_found:
        disp_header()
        print(txtbld+"\n Welcome "+studentname+txtrst)
        print()
        time.sleep(1)
    else:
        print_err("\n ERROR: Could not find student ID "+str(student))
        print_err("\n Total list scanned: "+str(count))
        sys.exit()
        
    return


# ========================================================================================
#  Search and find questions files v2
#  To be used for set of questions file1(q1,q1,..) + file2(q2,q2,..) + q3(...
#
def get_qfileset():

    global qfileset

    for name in glob.glob( S_filepref[tmode] + '*.txt'):
        qfileset.append( name )
    n = len( qfileset )    
    if n==0:
        print_err('Fatal error. Q files not found.')
        sys.exit(2)    
    qfileset.sort()                            # Ensure that the files are in order
    if _debug:
        for i in range( n ):
            print('Q file: ' + qfileset[i] )    
            
    return( n )


# ========================================================================================
#  Init qfileset
#
def init_qfileset():
    
    global qfileset

    for n in range( S_questions[tmode] ):
        qfileset.append( S_filepref[tmode] + str(n) + '.txt')
    if _debug:
        for i in range( n ):
            print('Q file: ' + qfileset[i] )    
            
    return( n )


# ========================================================================================
#  Load question text into current question buffer: qbuffer
#
def load_question_buffer( filename, qpick ):
    
    global qbuffer
    qbuffer = []                            # Empty the data buffer
    line    = []
    marker  = '<QUESTION>'
    markend = '</QUESTION>'
    state   = 'search' 
    inquote = False
    qindex = 0
    
    f = open_file(filename, 'r')
    ##print('Loading question buffer:'+filename)
    line = f.readline()
    while line:
        if state == 'search':
            if line.strip() == marker:
                qindex = qindex + 1
                print(line+'  '+str(qindex)+'  '+str(qpick))
                if qindex==int(qpick):
                    state = 'found'
                    print('Question '+str(qpick)+'/'+str(qindex)+' found' )
                #continue
                #else:
                #    continue
        else:            ### if state == 'found':
            if line.strip() == markend:
                print('Done buffering question '+str(qpick))
                if _debug: 
                    print('Question picked and buffered:')
                    for txt in qbuffer:
                        print(txt)
                return
            else:
                qbuffer.append( line )
        #print('2:')
        line = f.readline()
        #print('3:'+line)
    f.close()
    
    if state != 'found':
        print()
        print( txtemp+" ERROR: Question no.", qpick, "not available." )
        print( " ...... Ending program."+txtrst )
        wait_enter()
        sys.exit()    
    return
    
    
# ========================================================================================
#  Load all data in data bank targetted by Q# --> to remove later
#
def get_qbank_data( filename ):
    
    global qbankbuffer
    qbankbuffer = []                            # Empty the data buffer
    
    f = open_file(filename, 'r')
    line = f.readline()
    while line:
        qbankbuffer.append( line )
        line = f.readline()
    f.close()
    return
    

# ========================================================================================
# Find out the number of questions contained in the Qbank file
#
def get_qcount_from_file( filename ):
    
    f = open_file( filename, 'r')
    qcount = 0
    line = f.readline()
    while line:
        if line.strip() == "<QUESTION>":
            qcount = qcount+1
        line = f.readline()
    f.close()
    return qcount

    
# ========================================================================================
# Create status file, v2 
#
#   Status file format ('status.090'):
#
#    # mode e.g. ASSIGNMENT or LABTEST
#    # matrics  student name
#    1   x   4    yy/mm/dd    hh:mm:ss   <-- start time
#    2   x   4    yy/mm/dd    hh:mm:ss
#      3    x   4    yy/mm/dd    hh:mm:ss
#    4   x   4    yy/mm/dd    hh:mm:ss
#    0   0   0    yy/mm/dd    hh:mm:ss   <-- 0 0 0 = done!
#    ^   ^   ^
#    |   |   '-------- total Q to answer
#    |   '---------- qpick = random question from current file
#    '--------- Q # completed
#
def create_status_file_090():

    print(" Creating NEW status file...")
    cmdline = "mkdir " + workdir
    retval = os.system(cmdline)
    cmdline = "cd " + workdir
    retval = os.system(cmdline)
    cmdline = "mkdir " + xfrdir
    retval = os.system(cmdline)
    f = open_file(statusfile, 'w')
    timestamp = datetime.datetime.now()
    f.write('# ' + mode + '\n')
    f.write('# %s  %s\n' %(str(studentid), studentname))
    f.write('%d  %d  %d  %s\n' %(qcurrent, qpick, qtotal, timestamp))
    f.close()
    return


# ========================================================================================
#   Read the status of the student from status file, v2.1
#   Refer to create_status_file() for format of contents
#    "refix" the value of time_start read from the status file
#        It should be read from the first line of data 
#        (after skipping the top comments)        
#
def read_status_file_090():
    global qcurrent, qpick, qtotal

    print(" Reading status file...")
    f = open_file(statusfile, 'r')
                                            
    firstlineread = False
    line = f.readline()
    while line:
        if line[0]!='#':                    # Ignore comment lines
            words = line.split()
            if not firstlineread:            # First data line contains...
                firstlineread = True
                q_date = words[3]            # Get start date
                q_time = words[4]            # Get start time
        if _debug: print( line )
        line = f.readline()         
    f.close()                        
                                            # Last line contains...
    q_no = words[0]                         # current question # (n)
    q_pick = words[1]                        # question randomly picked from file (xx)
    q_max = words[2]                        # Total questions to answer (N)

    t = q_date + " " + q_time
    t = time.strptime(t[:19], '%Y-%m-%d %H:%M:%S')
    if _debug: print( t )
    st_time = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

    if int(q_no) == 0:
        print( txthlt + "\n No more question to answer. You are done.\n"+txtrst )
        sys.exit()
    else:
        qcurrent = int(q_no)
        qpick = int(q_pick)
        qtotal = int(q_max)
        print(" Current question number:", qcurrent, "out of", qtotal )
    return st_time


# ========================================================================================
# Update status file. Called when a queston is completed (answer submitted)
#    
def update_status_file():
            
    f = open_file(statusfile, 'a')
    timestamp = datetime.datetime.now()
    f.write("%d  %d  %d  %s\n" % (qcurrent, qpick, qtotal, timestamp))
    f.close()
    return


# ========================================================================================
# Display question V3 -- use buffered data
#
def disp_question_buffer():

    marker  = '<QUESTION>'
    markend = '</QUESTION>'

    if _debug: print('disp_question', qcurrent)
    disp_header()
    print( bakwht+bldblu+'                                 Question '+str(qcurrent)+' of '+str(qtotal)+'                               '+txtrst+'\n' )
    for line in qbuffer:
        if line.strip() != marker and line.strip() != markend:
            line = line.replace('<em>', txtemp)
            line = line.replace('</em>', txtrst)
            line = line.replace('<b>', txtbld)
            line = line.replace('</b>', txtrst)
            line = line.replace('<u>', txtund)
            line = line.replace('</u>', txtrst)
            line = line.replace('<code>', txtcod)
            line = line.replace('</code>', txtrst)
            print( line, end='' )
    print( bakwht+bldblu+'                                End of Question                                '+txtrst )
    return
    

# ========================================================================================
# Display question V2
#
def disp_question( questno ):

    if _debug: print('disp_question', questno)

    disp_header()

    marker  = '<QUESTION>'
    markend = '</QUESTION>'
    state   = 'search' 
    inquote = False
    
    qindex = 0
    for line in qbankbuffer:
        if state == 'search':
            if line.strip() == marker:
                qindex = qindex + 1
                if qindex==int(questno):
                    print( bldcyn+"[Question: "+str(qcurrent)+"]"+txtrst )
                    print()
                    state = 'found'
                    continue
            else:
                continue
        elif state == 'found':
            if line.strip() == markend:
                print( bldcyn+"[End of Question "+str(qcurrent)+" of "+str(qtotal)+"]"+txtrst )
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
    
    if state != 'found':
        print()
        print( txtemp+" ERROR: Question no.", questno, "not available." )
        print( " ...... Ending program."+txtrst )
        wait_enter()
        sys.exit()
    
    return
    
    
# ========================================================================================
#  Display prompt and get command from user
#
def prompt():

    global time_over

    now = datetime.datetime.now()
    rt = check_time_over( now )
    lapsed = now - time_start
    
    if rt=='TIME_OVER':
        print('\n')
        print_err(' Sorry, your time is up. Session has ended. ')
        print_msg('\nAttempting to submit your current answer') 
        submit_answer( qcurrent )
        cleanup_exit()
            
    if rt=='IN_TIME':
        remain = time_limit - now
        print(bakblu+' '+str(remain)[0:7]+' '+txtrst+bldblu+' Option/Command > '+txtrst, end='')
    else:                                    #if rt=='EXTRA_TIME':
        beep()
        remain = time_extra - now    
        print( txtemp + ' Time is up, please submit your answer. Session will end in about ' 
                      + str(remain.seconds) + ' seconds' + txtrst )
        print( bakred+' '+str(lapsed)[0:7]+' ===> '+txtrst, end='' )
    
    sys.stdout.flush()
    i, o, e = select.select( [sys.stdin], [], [], 10 )
    if (i):
        return sys.stdin.readline().strip().lower()
    else:
        return ''


# ========================================================================================
#  Check if time limit is over
#
def check_time_over( now ):

    if _debug:
        print('Now   = ' + str(now) )
        print('Start = ' + str(time_start) )
        print('Limit = ' + str(time_limit) )
        print('Extra = ' + str(time_extra) )

    if now < time_limit:
        return 'IN_TIME'
    elif now < time_extra:
        return 'EXTRA_TIME'
    else:
        return 'TIME_OVER'
    
    
# ========================================================================================
#  Wait for user to press ENTER 
#
def wait_enter():
    
    print('\n Press '+txtbld+'[Enter]'+txtrst+' to continue ', end='')
    try:
        entry = raw_input()   # for python 2.x
    except:
        entry = input()
    return


# ========================================================================================
#  Open file with supplied name and mode
#
def open_file(filename, opmode):

    """Open a file, check for error"""
    if _debug: print('Opening', filename, opmode)
    try:
        the_file = open(filename, opmode)
    except(IOError) as e:
        print_err(" ERROR: Unable to open the file "+filename)
        print_err(e)
        print_err(" Ending program.\n")
        input("\n Press [Enter] to exit.")
        sys.exit()
    else:
        return the_file


# ========================================================================================
# Next question V2
# Move to next question, pick qtext from qfile and buffer into qbuffer
#
def next_question():
    
    global qcurrent, qpick, qtotal, all_done, qfilename

    if qcurrent < qtotal:
        qcurrent = qcurrent + 1                        # Advance to next Q#    
        qfilename = qfileset[qcurrent-1]            # Get the filename
        n = get_qcount_from_file( qfilename )        # Count how many Qs in the Qbank file
        qpick = random.randint(1,n)                    # Pick single Q position from the whole Qbank    
        load_question_buffer( qfilename, qpick )    # Buffer the contents of question text
        print(" Current question number: ", qcurrent, "(out of ", qtotal, " questions)")        
        if _debug:
            print('next_question():', qfilename, qcurrent, qpick)            
    else:
        qcurrent = 0
        qpick = 0
        qtotal = 0
        disp_header()
        print( '\n\n'+ txthlt + " Congratulations! You're done!\n" + txtrst)
        all_done = True
    print()
    return
    
"""
# ========================================================================================
# Move to next question by updating relevant global variables
#
def next_question():
    
    global qcurrent, qpick, qtotal, all_done, qfilename

    if qcurrent < qtotal:
        qcurrent = qcurrent + 1                # Advance to next Q#    
        qfilename = qfileset[qcurrent-1]    # Get the filename
        get_qbank_data( qfilename )            # Buffer the contents of the Qbank file
        n = get_qcount()                    # Count how many Qs in the Qbank
        qpick = random.randint(1,n)            # Pick single Q position from the whole Qbank    
        print(" Current question number: ", qcurrent, "(out of ", qtotal, " questions)")        
        if _debug:
            print('next_question():', qfilename, qcurrent, qpick)            
    else:
        qcurrent = 0
        qpick = 0
        qtotal = 0
        disp_header()
        print( '\n\n'+ txthlt + " Congratulations! You're done!\n" + txtrst)
        all_done = True
    print()
    return
"""

# ========================================================================================
# View all questions in the Qfile
#
def view_all_questions( filename ):
    
    get_qbank_data( filename )
    questmax = get_qcount()
    print('Total Q in file ', questmax )
    for questno in range( 1, questmax+1 ):
        disp_question( questno )
        wait_enter()
    return


# ========================================================================================
# Display nice little title header
#
def disp_header():

    if tmode=='asgn1':
        hdrcolor = bakblu+bldwht
        title = " =                           LAB ASSIGNMENT / QUIZ 1                          ="
    elif tmode=='asgn2':
        hdrcolor = bakblu+bldwht
        title = " =                           LAB ASSIGNMENT / QUIZ 2                          ="
    elif tmode=='asgn3':
        hdrcolor = bakblu+bldwht
        title = " =                           LAB ASSIGNMENT / QUIZ 3                          ="        
    elif tmode=='labtest1':
        hdrcolor = bakblu+bldylw
        title = " =                       P R A C T I C A L   T E S T   1                      ="
    elif tmode=='labtest2':
        hdrcolor = bakblu+bldylw
        title = " =                       P R A C T I C A L   T E S T   2                      ="
    else:
        hdrcolor = bakcyn+bldwht
        title = " =                              PRACTICE SESSION                              ="
    
    os.system("clear")
    print( hdrcolor+" =SPI-LT "+version+"==============================================================")
    print(" =                       UNIVERSITI TEKNOLOGI PETRONAS                        =")
    print(" =            Department of Electrical and Electronic Engineering             =")
    print(" =              EDB1023 Structured Programming and Interfacing                =")
    print( title )
    print(" =============================================================================="+txtrst)
    print( crsrup+hdrcolor+"=========================================================================("+str(qcurrent)+"/"+str(qtotal)+")")
    print( crsrup+' ='+studentname+txtrst )
    return
    

# ========================================================================================
# Display the help page
#
def disp_help():

    disp_header()
    print()
    print(" o Please observe the following steps:")
    print()
    print("   1. "+txtund+"V"+txtrst+txtbld+"iew"+txtrst+" current question ("+ str(qcurrent) +" out of "+ str(qtotal) +")")
    print("   2. "+txtund+"E"+txtrst+txtbld+"dit"+txtrst+" your program/answer")
    print("   3. "+txtund+"C"+txtrst+txtbld+"ompile"+txtrst+" your program")
    print("   4. "+txtund+"R"+txtrst+txtbld+"un"+txtrst+"/execute your program")
    print("   5. Verify that the program and its output answers the question correctly")
    print("      Repeat any of the above steps until you are satisfied with your work")
    print("   6. "+txtund+"S"+txtrst+txtbld+"ubmit"+txtrst+" your program to proceed to next question")
    print()
    print(" o Questions must be answered in order. Once an answer is submitted, the ")
    print("   question CANNOT be viewed anymore")
    return


# ========================================================================================
# Display a short version of help i.e. list of options only
#
def disp_short_help():
    #print( bakblu+'                                                                            '+str(duration)+' '+txtrst)
    print( bakblu+" Options:   " +txtund+"h"+txtrst+bakblu+"elp  " +
            txtund+"v"+txtrst+bakblu+"iew  " +txtund+"e"+txtrst+bakblu+"dit  " +
            txtund+"c"+txtrst+bakblu+"ompile  " +txtund+"r"+txtrst+bakblu+"un  " +
            txtund+"s"+txtrst+bakblu+"ubmit  " + "e"+txtund+"x"+txtrst+bakblu + "it                    " +
            str(duration)+' '+txtrst)
    """    
    print( bakblu+" Options:   " +txtund+"h"+txtrst+"elp  " +txtund+"v"+txtrst+"iew  " +
            txtund+"e"+txtrst+"dit  " +txtund+"c"+txtrst+"ompile  " +
            txtund+"r"+txtrst+"un  " +txtund+"s"+txtrst+"ubmit  " +
            "e"+txtund+"x"+txtrst+"it           "+str(duration)+' '+txtrst)
    """
    return


# ========================================================================================
# Call external editor to edit current program
#
def edit_program():

    progname = 'program'+str(qcurrent).strip()+'.c'
    fullprogname = workdir+progname
    if _debug: print('Afile', fullprogname, '#', qcurrent)

    # If file does not exist, create new
    if not os.path.isfile(fullprogname):
        create_new_program( fullprogname, progname )

    # If file succesfully created or already exist, open it
    if os.path.isfile(fullprogname):                    
        print_msg(' Opening program file in a new window...')
        os.system('gedit ' + fullprogname + ' + &')
        print_msg(' Program file '+progname+' opened for editing in another window.')
    return


# ========================================================================================
# Create a new C program file to contain answer for current question V2
#
def create_new_program( fullprogname, progname ):

    now = datetime.datetime.now()
    print(' Creating file', fullprogname)
    fo = open_file(fullprogname, 'w')
    fo.write('/*****************************************************************************\n')
    fo.write(' * '+str(studentid)+' '+studentname+' '+tmode+' '+progname+'\n')
    fo.write(' * '+str(now)[0:19]+'  '+str(time_start)+' @'+HOSTNAME+'\n')
    fo.write(' *----------------------------------------------------------------------------\n')                                                       
    #fi = open_file(qfilename, 'r')              # copy question as comment's content into file
    if _debug: print('Qfile', qfilename, '#', qcurrent)

    marker  = '<QUESTION>'
    markend = '</QUESTION>'

    qindex = 0
    for line in qbuffer:
        if _debug: print(line)
        if line.strip() != marker and line.strip() != markend:
            line = line.replace('<em>','')
            line = line.replace('</em>','')
            line = line.replace('<b>','')
            line = line.replace('</b>','')
            line = line.replace('<u>','')
            line = line.replace('</u>','')
            line = line.replace('<code>','')
            line = line.replace('</code>','')
            fo.write(' * '+line)
    fo.write(' *-----------------------------------------------------------------------------\n')
    fo.write(' * Your answer is only VALID if this WHOLE SECTION is fully intact\n')
    fo.write(' ******************************************************************************/\n\n')
    fo.write('#include <stdio.h>\n\n')
    fo.close()
    return


# ========================================================================================
# Call gcc to compile current program file
#
def compile_program( questno ):
    
    if os.path.isfile('a.out'):  
        os.system('rm a.out')                # Delete the older executable
        
    progfile = 'program'+str(questno).strip()+'.c'
    fullprogname = workdir+progfile
    print_msg('\n Compiling '+progfile+'...')
    cmdline = 'gcc '+fullprogname+ ' -lm' 
    retval = os.system(cmdline)
    if retval==0:
        cmdline = 'gcc -Wall '+fullprogname+ ' -lm' 
        os.system(cmdline)
        print_msg(' Program compiled successfully.\n')
    else:
        print_err(' Please check your program ')

    return retval


# ========================================================================================
# Use system call to run the executable program 
#
def run_program():
    
    if os.path.isfile('a.out'):  
        print(bakwht+bldgrn+' ----------------------------- Executing Program ----------------------------- '+txtrst)
        os.system('./a.out')
        print(bakwht+bldred+'\n ------------------------- End of Program Execution -------------------------- '+txtrst)
    else:
        print_err(' Unable to execute your program, please compile it first ')
    return


# ========================================================================================
# Get user confirmation for answer submission 
#
def confirm_submit( questno ):

    if _debug:
        print('SUBMIT', qfilename, qcurrent)

    print( txtbld+"\n You chose to submit your answer.\n Are you sure?"+txtrst)
    print(" Please enter "+txtbld+"y"+txtrst+" or "+txtbld+"n"+txtrst+" >> ", end='')
    try:
        reply = raw_input()
    except:
        reply = input()
    if reply=='y' or reply=='Y':
        if compile_program(questno)==0:
            return True
        else:
            print( txtemp+' Compilation error. Answer is NOT submitted.\n'+txtrst)
            print( txtemp+' Please check your program and try again.\n'+txtrst)
            return False
    else:
        return False


# ========================================================================================
# Copy the answer over to the server
#   Fixing the file copy routine:
#       Copy and rename as needed
#
def submit_answer(questno):

    progfile = 'program'+str(questno).strip()+'.c'
    print( txtbld+" Submitting", progfile, "to server..."+txtrst)

    fullprogname = workdir+progfile    
    srvfname = tmode + '/' + str(studentid) +'.' + progfile
    rc = socket_send_file( fullprogname, srvfname )        # Send a copy via socket
    if rc != 0:
        print_err('Unable to send '+progfile+' to server')

    print( txtbld+" Transferring a backup copy of " + progfile +txtrst)
    xfrfilename = xfrdir+'answer'+str(questno)+'.c'
    count = 0
    while True:
        rc = os.system('cp -f '+ fullprogname +'  '+ xfrfilename)    # Copy the file 
        if rc:
            print(" Error copying file")
            count = count + 1
            if count < 10:
                xfrfilename = xfrdir+'answer'+str(questno)+'.'+str(count).strip()+'.c'
                print(' Trying to copy with a new name = ', xfrfilename )
            else:
                print(' Gave up after trying so many times' )
                print_err(' Call for help!!!!')
                sys.exit()
        else:
            break
    
    print( txtbld+" OK."+txtrst)
    wait_enter()
    return 0


# ========================================================================================
#  Sending a copy of the answer to server via socket
#  Having problem at server side: filename and file contents are read together as one.
#  Trying to fix this by having a fixed length (40 chars) for filename
#
def socket_send_file( fullprogname, xfrname ):
    
    host = SERVERNAME
    #host = socket.gethostname()     # For debuggin... get local machine name
    port = 12345                     # Reserve a port for your service.

    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((host,port))
    except OSError as e:
        print("Could not open socket, ", e.strerror)
        print("Error code: ", e.errno)
        return 1

    # Fix length of xfrname to 40 chars
    n = len( xfrname )
    for i in range(40 - n):
        xfrname = xfrname+' '
    s.send( xfrname.encode() ) #s.send( xfrname )
    ack = ''
    time.sleep(1)   #ack = s.recv(1024)
    print('['+ack+']\n Sending...')
    f = open( fullprogname,'rb')
    l = f.read(1024)
    while (l):
        print(' ...')
        s.send(l)
        l = f.read(1024)
    f.close()
    print(" Done Sending")
    #time.sleep(3)   #ack = s.recv(1024)
    s.close 
    print('['+ack+']')
    return 0                


# ========================================================================================
#  Issue system (terminal) command for other options entered by user  
#
def os_command(line):
    print(" Passing the command to the OS...")
    retval = os.system(line)
    print(" Return value = " + str(retval) )
    disp_short_help()


# ========================================================================================
#  Get confirmation when user chose 'exit'
#
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


# ========================================================================================
#  Print normal message in bright colour
#
def print_msg( data ):
    
    print(txtbld+data+txtrst)
    return


# ========================================================================================
#  Print and highlight error message
#
def print_err( data ):
    
    for i in range(3):
        sys.stdout.write(txtemp+' E R R O R                                                   \r'+txtrst)
        sys.stdout.flush()
        time.sleep(0.5) 
        sys.stdout.write(txthlt+data+txtrst+'\r')
        sys.stdout.flush()
        time.sleep(0.5)
    print('\n')
    return


# ========================================================================================
#  Just produce a beep
#
def beep():

    print( '\a'+crsrup )
    return


# ========================================================================================
#  Clean up and exit
#        
def cleanup_exit():
        
    print("\n Removing temporary files...")
    os.system("cd ~")
    cmdline = "rm -r "+workdir
    if _debug: print( cmdline )
    os.system( cmdline )
    #os.system("clear")
    print( txtbld+"\n Thank You.\n"+txtrst )
    sys.exit()


# ========================================================================================
# Escape codes for colours 
#
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

txtbld=bldylw
txtemp=bldred
txtund=undylw+bldylw
txtcod=bldgrn
txthlt=bakred+bldwht
txtmsg=txtgrn
          

# ========================================================================================
# Entry point of program execution, call main()
#
if __name__ == "__main__":
   main(sys.argv[1:])
#
# End of program
# ========================================================================================
