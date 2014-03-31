#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Message box dialog with Whiptail.
###

## Arguments
title=$1
message=$2
height=$3
width=$4

whiptail --backtitle "OFELIA Control Framework" --title "$title" --msgbox "$message" $height $width
