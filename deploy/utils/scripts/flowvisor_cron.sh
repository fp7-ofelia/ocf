#!/bin/bash

RESULT=`/bin/ps aux | /bin/grep flowvisor | /bin/grep java | /bin/grep -v flowvisor_cron | /bin/grep -v grep`
FLOWVISOR_LOG=/var/log/flowvisor/flowvisor-stderr.log

if [ "$RESULT" == "" ]; then
  if [ -f $FLOWVISOR_LOG ]; then
      echo "[`date`] FlowVisor has failed" >> $FLOWVISOR_LOG
  fi
  if [ -f /etc/init.d/flowvisor ]; then
    /etc/init.d/flowvisor start
  else
    /usr/local/sbin/flowvisor /usr/local/etc/flowvisor/config.xml > /dev/null 1>&2 &
  fi
  if [ -f $FLOWVISOR_LOG ]; then
      echo "[`date`] FlowVisor restarted" >> $FLOWVISOR_LOG
  fi
else
  echo "FlowVisor is OK..."
fi
