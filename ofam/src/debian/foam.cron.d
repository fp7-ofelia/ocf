#
# Regular cron jobs for the foam package
#
0 *	* * *	www-data [ -x /opt/ofelia/ofam/local/bin/expire ] && /opt/ofelia/ofam/local/bin/expire
40 0,6,12,18 * * *  www-data [ -x /opt/ofelia/ofam/local/bin/expire-emails ] && /opt/ofelia/ofam/local/bin/expire-emails
0 3 * * * www-data [ -x /opt/ofelia/ofam/local/bin/daily-queue ] && /opt/ofelia/ofam/local/bin/daily-queue
