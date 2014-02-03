#!/bin/bash

###
#   @author: CarolinaFernandez
#   @organization: i2CAT
#   @project: OFELIA FP7
#   @description: Common entry point for installation
###

## Arguments
whiptail_args=$@
num_whiptail_args=$#
# Replace all "[", "]", "," by a space
whiptail_args=${whiptail_args//[\[\]\,]/ }
# Create array from list
whiptail_args=($whiptail_args)

## Return code
confirm_install=0

## Parameters for whiptail screen
whiptail_width=45
whiptail_checklist_title="OCF installation"
whiptail_checklist_description="Choose the modules by pressing SPACE key and finally entering <Ok>"
whiptail_checklist_options=""
whiptail_message_title="Installation stopped"
whiptail_message_description="You have stopped or cancelled the installation"

function exit_on_null_arg()
{
    if [[ $1 == "" ]]; then
        whiptail --title "$whiptail_message_title" --msgbox "$whiptail_message_description" 8 $whiptail_width
        confirm_install=1
        exit $confirm_install
    fi
}

function main()
{
    for i in "${whiptail_args[@]}"
    do
        whiptail_checklist_options="$whiptail_checklist_options $i '' false"
    done
    
    ocf_modules_install=""
    while [ $confirm_install -eq 0 ]; do
        ocf_modules_install=$(whiptail --checklist "$whiptail_checklist_description" $(($num_whiptail_args*3)) $whiptail_width $num_whiptail_args $whiptail_checklist_options --title "$whiptail_checklist_title" 3>&1 1>&2 2>&3)
        #ocf_modules_install=$?
        # Saving the return code (0/1)
        exit_on_null_arg $ocf_modules_install
        
        ocf_modules_install_exitcode=$(echo $ocf_modules_install | rev | cut -d "\"" -f1)
        # Removing the return code
        ocf_modules_install=$(echo $ocf_modules_install | head -c -2)
        # If installation is cancelled (ocf_modules_install_exitcode != 0), no further step is loaded
        exit_on_null_arg $ocf_modules_install
        
        # Formatting the chosen OCF modules to show in a confirm box
        ocf_modules_install_confirmed=""
        ocf_modules_install_confirmed_set=($ocf_modules_install)
        num_ocf_modules_install_confirmed_set=${#ocf_modules_install_confirmed_set[@]}
        if [[ num_ocf_modules_install_confirmed_set -eq 0 ]]; then
            num_ocf_modules_install_confirmed_set=1
        fi
        
        for i in "${ocf_modules_install_confirmed_set[@]}"
        do
            # Remove quotes from module names also
            ocf_modules_install_confirmed="$ocf_modules_install_confirmed *${i//[\"]/ }\n"
        done
        
        whiptail --yesno "You are going to install the following modules:\n\n$ocf_modules_install_confirmed" $(($(($num_ocf_modules_install_confirmed_set+4))*2)) $whiptail_width
        confirm_install=$?
        # Negate exit code (whiptail --yesno => yes: 1, no: 0)
        confirm_install=$((! $confirm_install ))
    done
    # Write file to be parsed later
    echo $ocf_modules_install > ocf_modules_install
}

main $@
return_code=$?
exit $return_code
