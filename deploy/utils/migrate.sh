#!/bin/bash

###
#       @author: msune, CarolinaFernandez
#       @organization: i2CAT
#       @project: Ofelia FP7
#       @description: Shell migration file 
###


### Import to use other functions
source utils.sh

function update_apache_symlinks()
{
    current_ocf_path=$1
    new_ocf_path=$2
    
    APACHE_SITES_AVAILABLE=/etc/apache2/sites-available
    sites_available=$(ls -la $APACHE_SITES_AVAILABLE)
    
    print_header "Updating symlinks under Apache ($APACHE_SITES_AVAILABLE)..."
    for f in $sites_available; do
        f=$APACHE_SITES_AVAILABLE/$f
        if [[ -L "$f" && -f "$f" ]]; then
            current_link=$(readlink $f)
            if [[ $current_link == *$current_ocf_path* ]]; then
                new_link=$(echo $current_link | sed -e "s|${current_ocf_path}|${new_ocf_path}|g")
                echo "Unlinking old file: $current_link"
                rm $f
                echo "Relinking new file: $new_link"
                ln -s $new_link $f
            fi
        fi
    done

    APACHE_SITES_CONFD=/etc/apache2/conf.d
    sites_available=$(ls -la $APACHE_SITES_CONFD)

    print_header "Updating symlinks under Apache ($APACHE_SITES_CONFD)..."
    for f in $sites_available; do
        f=$APACHE_SITES_CONFD/$f
        if [[ -L "$f" && -f "$f" ]]; then
            current_link=$(readlink $f)
            if [[ $current_link == *$current_ocf_path* ]]; then
                new_link=$(echo $current_link | sed -e "s|${current_ocf_path}|${new_ocf_path}|g")
                echo "Unlinking old file: $current_link"
                rm $f
                echo "Relinking new file: $new_link"
                ln -s $new_link $f
            fi
        fi
    done
}

function update_framework_envvars()
{
    # Update value for environment variable: OCF_PATH
    current_ocf_path=$1
    new_ocf_path=$2
    
    # Set environment variables in Apache's envvars file
    APACHE_ENVVARS=/etc/apache2/envvars
    if [ -f $APACHE_ENVVARS ]; then
        if [ -z $(grep -q $OCF_PATH $APACHE_ENVVARS) ]; then
            print_header "Updating Apache env vars ($APACHE_ENVVARS)..."
            # Using different delimiters, as "/" is used within OCF_PATH
            sed -i "s|OCF_PATH=$OCF_PATH|OCF_PATH=$new_ocf_path|g" $APACHE_ENVVARS
        fi
    fi
    
    # Set environment variables under OS's profile.d folder
    PROFILE_D=/etc/profile.d
    PROFILE_D_OCF=$PROFILE_D/ocf.sh
    if [ -d $PROFILE_D ]; then
        if [ -f $PROFILE_D_OCF ]; then
            print_header "Updating Unix env vars ($PROFILE_D_OCF)..."
            # Using different delimiters, as "/" is used within OCF_PATH
            sed -i "s|OCF_PATH=$OCF_PATH|OCF_PATH=$new_ocf_path|g" $PROFILE_D_OCF
        fi
    fi
}

function validate_new_ocf_path()
{
    new_ocf_path=$1

    # Ensure the new path ends with a "/"
    last_char=${new_ocf_path#${new_ocf_path%?}}
    if [[ $last_char != "/" ]]; then
        new_ocf_path=$new_ocf_path/
    fi

    # Ensure the path for the migration still does not exist
    if [ -d $new_ocf_path ]; then
        error "Path '$new_ocf_path' already exists. Migration cannot be completed"
    fi
}

function migrate_framework()
{
    # Identify current value for OCF_PATH to move symlinks
    current_ocf_path=$OCF_PATH
    new_ocf_path=$1
    validate_new_ocf_path $new_ocf_path
    if [ -d $current_ocf_path ]; then
        cp -Rp $current_ocf_path $new_ocf_path
        update_apache_symlinks $current_ocf_path $new_ocf_path
        update_framework_envvars $current_ocf_path $new_ocf_path
        # XXX Uncomment after testing
        #rm -r $current_ocf_path
    fi
}

migrate_framework $@

