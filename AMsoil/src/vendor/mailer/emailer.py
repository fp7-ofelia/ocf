import smtplib
from email.mime.text import MIMEText

from amsoil.core import pluginmanager as pm
from amsoil.core import serviceinterface
from amsoil.core.exception import CoreException
import amsoil.core.log
logger=amsoil.core.log.getLogger('mailer')

"""
Currently only unsecure connections to smtp servers are supported.
"""

class Mailer(object):
    @serviceinterface
    def __init__(self, default_sender, host, port=25, use_tls=False, username=None, password=None):
        """
        {default_sender} email adress to use for the From: field when sending mails (unless otherwise specified).
        {host}, {port} connection information for the smtp server.
        {use_tls} Enables encryption when talking to the smtp server.
        {username}, {password} credentials for authenticating with the smtp server.
        """
        self.default_sender, self.host, self.port, self.use_tls, self.username, self.password = default_sender, host, port, use_tls, username, password

    @serviceinterface
    def sendMail(self, receiver, subject, body, sender=None):
        """
        Send a plain-text mail {sender} an email to an {receiver}(s) with the given {subject} and {body}.
        {receiver} Python string or a list of strings. E.g. 'to.someone@example.com' or ['me@example.com', 'you@example.net']
        {subject} Python string.
        {body} Python string.
        {sender} None or Python string. If None is given the default sender from the connection will be used.
    
        This method will capture all errors. The method will return True if the sending was sucessful, False if an error occured.
        """
        if (not sender):
            sender = self.default_sender

        if type(receiver) is str:
            receiver = [receiver]
        try:
            # construct message
            message = MIMEText(body)
            message['Subject'] = subject
            message['From'] = "<%s>" % (sender,)
            message['To'] =  ', '.join(["<%s>" % (r,) for r in receiver])
            # establish connection
            con = smtplib.SMTP(self.host, self.port)
            con.ehlo()
            if self.use_tls:
                con.starttls()
                con.ehlo()
            if self.username:
                con.login(self.username, self.password)
            con.sendmail(sender, receiver, message.as_string())
            logger.info("Mail sent to [%s]" % (', '.join(receiver),))
            con.quit()
            return True
        except Exception as e:
            logger.error("Sending mail to %s failed (%s).\n\n%s" % (receiver, str(e), str(message)))
            return False
