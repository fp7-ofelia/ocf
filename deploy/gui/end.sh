#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Ending info screen dialog with Whiptail.
###

## Arguments
whiptail_action=$1
whiptail_action=${whiptail_action,,}
whiptail_message_title="OCF $whiptail_action"
whiptail_message_description="The $whiptail_action process has finished";

## Parameters for whiptail screen
whiptail_width=45

## Paths
gui_path="./deploy/gui"

.${gui_path}/info.sh "$whiptail_message_title finished" "$whiptail_message_description" "8" "$whiptail_width"
#exit 1
