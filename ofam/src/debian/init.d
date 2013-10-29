#! /bin/sh

### BEGIN INIT INFO
# Provides:          foam
# Required-Start:    $local_fs $network
# Required-Stop:     
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: GENI OpenFlow Aggregate Manager
# Description:       GENI OpenFlow Aggregate Manager
### END INIT INFO

# Author: Nick Bastin <nick.bastin@gmail.com>
#         Josh Smift <jbs@geni.net>

PATH=/sbin:/usr/sbin:/bin:/usr/bin
DAEMON=/opt/ofelia/ofam/local/sbin/foam.fcgi
NAME=foam
DESC=FOAM
PIDFILE=/var/run/$NAME.pid

#Make the package executable or if not there exit
chmod +x $DAEMON || exit 1
# Exit if the package is not installed
[ -x $DAEMON ] || exit 1

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Include general init vars
. /lib/init/vars.sh

# Include standard LSB functions
. /lib/lsb/init-functions

# Start function
do_start()
{
    export PYTHONPATH=/opt/ofelia/ofam/local/lib
    start-stop-daemon --start --make-pidfile --background --chuid www-data --quiet --pidfile $PIDFILE --exec $DAEMON -- $DAEMON_ARGS || return $?
}

# Stop function
do_stop()
{
    start-stop-daemon --stop --quiet --pidfile $PIDFILE || return $?
    rm -f $PIDFILE
}

# Status function
do_status()
{
    status_of_proc -p $PIDFILE "$DAEMON" "$NAME"
}

# Main body
case "$1" in
  start)
        # If FOAM is running (do_status has exit status 0), exit with
        # status 1; if we don't exit, start FOAM.
        do_status > /dev/null && exit 1
        do_start
        ;;
  stop)
        do_stop
        ;;
  restart|force-reload)
        do_stop
	do_start
        ;;
  status)
        do_status
        ;;
  *)
        echo "Usage: $0 {start|stop|restart|force-reload|status}" >&2
        exit 3
        ;;
esac

exit
