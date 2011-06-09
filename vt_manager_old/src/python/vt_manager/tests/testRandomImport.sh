$ cat > showfile
#!/bin/sh
#
#Script to import models in random order
#
for ((  i = 0 ;  i <= 3;  i++  ))
do
    echo "Importing for $i times"
    python manage.py shell
    pid = ps -all | grep python | awk '{print $4}' 
    echo pid
    kill SIGEXIT pid
done
