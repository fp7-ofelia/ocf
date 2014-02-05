#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Common entry point for installation and upgrade.
###

## Arguments
action_arg=$1
shift # Consume first argument
ocf_module=$@

## Parameters for whiptail screen
whiptail_width=45
case $action_arg in
    install )
        whiptail_message_title="OCF installation";
        ;;
    upgrade|update )
        whiptail_message_title="OCF upgrade";
        ;;
    remove )
        whiptail_checklist_title="OCF removal";
        ;;
    *)
        echo "Usage: ./splash [install | upgrade | update | remove]";
        exit 1;
        ;;
esac
whiptail_message_description="Continue to $action_arg module $ocf_module...";

function main()
{
    whiptail --title "$whiptail_message_title" --msgbox "$whiptail_message_description" 8 $whiptail_width
}

main $@
