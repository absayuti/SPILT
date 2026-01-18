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
echo " =              EFB1023 Structured Programming and Interfacing                ="
echo " =          (S)tructured (P)rogramming and (I)nterfacing (L)ab (T)est         ="
echo "==============================================================================="
echo
echo " Please enter one of the following options:"
echo 
while true; do
	echo "   1 = Quiz or Test"
	echo
	echo "   2 = Practice"
	echo
	read -p "  >" ans
    case $ans in
        [1] ) python3 /mnt/pub/spilt/spilt.09400.py --a1; break;;
        [2] ) python3 /mnt/pub/spilt/spilt.09400.py; break;;
        * ) echo " Please enter 1 or 2.";;
    esac
done

# Start SPILT for Assignment/Quiz #1
# mnt/pub/spilt/spilt09xxx.py --a1
#
#Start SPILT for Assignment/Quiz #2
#/mnt/pub/spilt/spilt09xxx.py --a2
#
# Start SPILT for Lab Test #1
# /mnt/pub/spilt/spilt09xxx.py --t1
#
# Start SPILT for Lab Test #2
# /mnt/pub/spilt/spilt09xxx.py --t2
#


