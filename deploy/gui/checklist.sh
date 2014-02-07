#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Checklist dialog with Whiptail.
###

## Arguments
title=$1
message=$2
height=$3
width=$4
list_num=$5
list_options=$6

whiptail --backtitle "OFELIA Control Framework" --title "$title" --checklist "$message" "$height" "$width" "$list_length" "$list_options"
