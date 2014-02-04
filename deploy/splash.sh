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
whiptail_args=$@
num_whiptail_args=$#
# Replace all "[", "]", "," by a space
whiptail_args=${whiptail_args//[\[\]\,]/ }
# Create array from list
whiptail_args=($whiptail_args)

## Return code
confirm_deploy=0

## Parameters for whiptail screen
whiptail_width=45
case $action_arg in
    install )
        whiptail_checklist_title="OCF installation";
        whiptail_message_title="Installation stopped";
        whiptail_message_description="You have stopped or cancelled the installation";
        ;;
    upgrade|update )
        whiptail_checklist_title="OCF upgrade";
        whiptail_message_title="Upgrade stopped";
        whiptail_message_description="You have stopped or cancelled the upgrade";
        ;;
    *)
        echo "Usage: ./splash [install | upgrade | update]";
        exit 1;
        ;;
esac
whiptail_checklist_description="Choose the modules by pressing SPACE key and finally entering <Ok>"
whiptail_checklist_options=""

function exit_on_null_arg()
{
    if [[ $1 == "" ]]; then
        whiptail --title "$whiptail_message_title" --msgbox "$whiptail_message_description" 8 $whiptail_width
        confirm_deploy=1
        exit $confirm_deploy
    fi
}

function main()
{
    for i in "${whiptail_args[@]}"
    do
        whiptail_checklist_options="$whiptail_checklist_options $i . false"
    done
    
    ocf_modules_deploy=""
    while [ $confirm_deploy -eq 0 ]; do
        ocf_modules_deploy=$(whiptail --checklist "$whiptail_checklist_description" $(($((2+$num_whiptail_args))*3)) $whiptail_width $num_whiptail_args $whiptail_checklist_options --title "$whiptail_checklist_title" 3>&1 1>&2 2>&3)
        #ocf_modules_deploy=$?
        # Saving the return code (0/1)
        exit_on_null_arg $ocf_modules_deploy
        
        ocf_modules_deploy_exitcode=$(echo $ocf_modules_deploy | rev | cut -d "\"" -f1)
        # Removing the return code
        ocf_modules_deploy=$(echo $ocf_modules_deploy | head -c -2)
        # If installation is cancelled (ocf_modules_deploy_exitcode != 0), no further step is loaded
        exit_on_null_arg $ocf_modules_deploy
        
        # Formatting the chosen OCF modules to show in a confirm box
        ocf_modules_deploy_confirmed=""
        ocf_modules_deploy_confirmed_set=($ocf_modules_deploy)
        num_ocf_modules_deploy_confirmed_set=${#ocf_modules_deploy_confirmed_set[@]}
        if [[ num_ocf_modules_deploy_confirmed_set -eq 0 ]]; then
            num_ocf_modules_deploy_confirmed_set=1
        fi
        
        for i in "${ocf_modules_deploy_confirmed_set[@]}"
        do
            # Remove quotes from module names also
            ocf_modules_deploy_confirmed="$ocf_modules_deploy_confirmed *${i//[\"]/ }\n"
        done
        
        whiptail --yesno "You are going to install the following modules:\n\n$ocf_modules_deploy_confirmed" $(($(($num_ocf_modules_deploy_confirmed_set+4))*2)) $whiptail_width
        confirm_deploy=$?
        # Negate exit code (whiptail --yesno => yes: 1, no: 0)
        confirm_deploy=$((! $confirm_deploy ))
    done
    # Write file to be parsed later
    echo $ocf_modules_deploy > ocf_modules_deploy
}

main $@
return_code=$?
exit $return_code
