#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Yes/no dialog with Whiptail.
###

## Arguments
message=$1
height=$2
width=$3

whiptail --backtitle "OFELIA Control Framework" --yesno "$message" $height $width
