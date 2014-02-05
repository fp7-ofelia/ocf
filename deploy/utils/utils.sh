#!/bin/bash

list_to_array()
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
