#!/bin/bash

###
#       @author: msune, CarolinaFernandez
#       @organization: i2CAT
#       @project: Ofelia FP7
#       @description: Shell utils file 
###


###I/O functions

##Output utils
txtrst=$(tput sgr0) # Text reset
txtred=$(tput setaf 1) # Red
txtgreen=$(tput setaf 2) # Green
txtylw=$(tput setaf 3) # Yellow
txtbold=$(tput bold) # Bold text

# Simple print
function print()
{
    if [ "$2" == 1 ]; then
        OUT="/dev/stderr"
    else
        OUT="/dev/stdout"
    fi
    echo -e "$1" > $OUT
}

# Make bold text
function print_bold()
{
    print "${txtbold} $@ ${txtrst}"
}

# Heading print
function print_header()
{
    print ""
    print ""
    print_bold "${txtgreen}$1 `print_bold $2`"
}

# Success
function success()
{
    print "${txtgreen}SUCCESS:${txtrst} $1"
}

# Warning
function warning()
{
    print "${txtylw}WARNING:${txtrst} $1"
}

# Error function; invoques restore
function error()
{
    print "${txtred}FATAL ERROR:${txtrst} $1"
    exit 1 
}

## INPUT UTILS

# Confirmation with exit
# Usage: $1: message, [$2 throw error on its presence $NO_RETURN], [$3 when $2 present, do not rollback; $NO_RESCUE]
function confirm()
{
    local VALUE
    while :
    do
        echo "$1. Do you confirm (Y/N)?"
        read VALUE
        if [ "$VALUE" == "Y" ] || [ "$VALUE" == "y" ]; then
            # Accepted
            return 0
        elif [ "$VALUE" == "N" ] || [ "$VALUE" == "n" ]; then
            # Rejected
            error "'$1' clause not confirmed. Aborting..." $3 
        fi
    done
}

function pause()
{
    echo $1
    echo -n "Press any key to continue..."
    read 
}

## FILE UTILS

# Recover directory path
function get_directory()
{
    echo `dirname $(readlink -f $1)`
}

## POST-PROCESSING

# Convert list (i.e. Python) to bash array
function list_to_array()
{
    list=$@
    # Replace all "[", "]", "," by a space
    string=${list//[\[\]\,]/ }
    # Create array from list
    array=($string)
    echo "$array"
}
#arr=$(list_to_array "['expedient', 'vt_manager']")
#echo "array: $arr"

