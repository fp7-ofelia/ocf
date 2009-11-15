import logging

#SFA access log initialization

SFA_ACCESS_LOGFILE='/var/log/sfa_access.log'
SFA_HTTPD_ACCESS_LOGFILE='/tmp/sfa_httpd_access.log'
logger=logging.getLogger()
logger.setLevel(logging.INFO)
try:
    logfile=logging.FileHandler(SFA_ACCESS_LOGFILE)
except IOError:
    # This is usually a permissions error becaue the file is
    # owned by root, but httpd is trying to access it. 
    logfile=logging.FileHandler(SFA_HTTPD_ACCESS_LOGFILE)
formatter = logging.Formatter("%(asctime)s - %(message)s")
logfile.setFormatter(formatter)
logger.addHandler(logfile)

def get_sfa_logger():
    return logger
