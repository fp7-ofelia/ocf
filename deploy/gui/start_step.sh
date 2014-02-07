#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Step to inform that an action over a module is about to take place.
###

## Arguments
action_arg=$1
shift # Consume first argument
ocf_module=$@

## Paths
gui_path="./deploy/gui"

## Parameters for whiptail screen
case $action_arg in
    install )
        message_title="OCF installation";
        ;;
    upgrade|update )
        message_title="OCF upgrade";
        ;;
    remove )
        message_title="OCF removal";
        ;;
    *)
        echo "Usage: ./start_step {install | upgrade | update | remove} <module>";
        exit 1;
        ;;
esac
message_description="Continue to $action_arg module $ocf_module...";

.${gui_path}/info.sh "$message_title" "$message_description" "8" "45"
