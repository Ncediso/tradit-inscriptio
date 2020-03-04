import re
import os
import logging
import inspect
import smtplib
import itertools
import mimetypes
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart


logger = logging.getLogger(__name__)
IS_PRODUCTION = True


def display_arguments(func):
    """
    This function displays the parameters and the values given to a function. This may be useful for debugging.
    :param func: Function
    :return: Function
    """

    def display_and_call(*args, **kwargs):
        # If you want arguments names as a list:
        args_name = inspect.getargspec(func)[0]

        # If you want names and values as a dictionary:
        args_dict = dict(itertools.izip(args_name, args))

        # If you want values as a list:
        # args_values = args_dict.values()

        if kwargs.keys():
            message = "Calling {} with arguments {} and named arguments {}."
            logger.debug(message.format(func.func_name, str(args_dict), str(kwargs)))
        else:
            message = "Calling {} with arguments {} and has no named arguments."
            logger.debug(message.format(func.func_name, str(args_dict)))
        return func(*args, **kwargs)

    return display_and_call


class CustomEmailService:
    """
    This class handles the creation and sending of email messages
    via SMTP.  This class also handles attachments and can send
    HTML messages.  The code comes from various places around
    the net and from my own brain.
    """

    def __init__(self, smtp_server):
        """
        Create a new empty email message object.

        @param smtp_server: The address of the SMTP server
        @type smtp_server: String
        """
        self._text_body = None
        self._html_body = None
        self._to = None
        self._from = None
        self._cc = None
        self._attach = None
        self._subject = ""
        self._smtp_server = smtp_server
        self._image_path = ""
        self._reEmail = re.compile(
            ("^([\\w \\._]+\\<[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}"
             "~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])"
             "?\\>|[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9]"
             "(?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$"))
        self.clear_recipients()
        self.clear_attachments()
        self.clear_cc_recipients()

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, email_subject):
        """
        Set the subject of the email message.
        """
        self._subject = email_subject

    @property
    def sender(self):
        return self._to

    @sender.setter
    def sender(self, email_address):
        """
        Set the email sender.
        """
        if not self.validate_email_address(email_address):
            raise Exception("Invalid email address '%s'" % email_address)
        self._from = email_address

    def set_image_path(self, file_path):
        """
        Set the image path.
        """
        if not self.validate_file_path(file_path):
            raise Exception("Invalid file path '%s'" % file_path)
        self._image_path = file_path

    def clear_recipients(self):
        """
        Remove all currently defined recipients for
        the email message.
        """
        self._to = []

    def clear_cc_recipients(self):
        """
        Remove all currently defined recipients for
        the email message.
        """
        self._cc = []

    def clear_attachments(self):
        """
        Remove all file attachments.
        """
        self._attach = []

    def add_recipient(self, address):
        """
        Add a new recipient to the email message.
        """
        if not self.validate_email_address(address):
            raise Exception("Invalid email address '%s'" % address)
        self._to.append(address)

    def add_cc_recipient(self, address):
        """
        Add a new cc recipient to the email message.
        """
        if not self.validate_email_address(address):
            raise Exception("Invalid email address '%s'" % address)
        self._cc.append(address)

    def add_attachment(self, attachment_full_path, attachment_name=None):
        """
        Add a file attachment to this email message.
        :param attachment_full_path: The full path and file name of the file
                                    to attach.
        :type attachment_full_path: String
        :param attachment_name: This will be the name of the file in the email message if set.  If not set
                                then the filename will be taken from the attachment_full_path parameter above.
        :type attachment_name: String
        """
        if (attachment_full_path is None
                or not self.validate_file_path(attachment_full_path)
                or not self.validate_file(attachment_full_path)):
            message = "The supplied path is not a file path or does not exist. Path: {}"
            logger.warning(message.format(attachment_full_path))
            return
        self._attach.append((attachment_full_path, attachment_name))

    def set_text_body(self, body):
        """
        Set the plain text body of the email message.
        """
        self._text_body = body

    def set_html_body(self, body):
        """
        Set the HTML portion of the email message.
        """
        self._html_body = body

    def validate_email_address(self, address):
        """
        Validate the specified email address.

        :return: True if valid, False otherwise
        :rtype: Boolean
        """
        if self._reEmail.search(address) is None:
            return False
        return True

    @staticmethod
    def validate_file_path(file_path):
        """
        Validate the specified file path.
        :param file_path: String
        :return: True if valid, False otherwise
        :rtype: Boolean
        """

        if not os.path.exists(file_path):
            return False
        return True

    @staticmethod
    def validate_file(file_path):
        """
        Validate the specified path is a file.
        :param file_path: String
        :return: True if valid, False otherwise
        :rtype: Boolean
        """

        if not os.path.isfile(file_path):
            return False
        return True

    def send(self):
        """
        Send the email message represented by this object.
        """

        try:
            # Validate message
            # logger.info("I am in the first section to send an email")
            if self._text_body is None and self._html_body is None:
                logger.error("Error! Must specify at least one body type (HTML or Text)")
                raise Exception("Error! Must specify at least one body type (HTML or Text)")
            if len(self._to) == 0:
                logger.error("Must specify at least one recipient")
                raise Exception("Must specify at least one recipient")

            # Create the message part
            if self._text_body is not None and self._html_body is None:
                msg = MIMEMultipart("alternative")
                logger.info("This is a plain message")
                msg.attach(MIMEText(self._text_body, "plain"))
            elif self._text_body is None and self._html_body is not None:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(self._html_body, "html"))
                logger.info("This is an html message")
            else:
                logger.info("This is an Alternative message")
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(self._text_body, "plain"))
                msg.attach(MIMEText(self._html_body, "html"))

            # Add attachments, if any
            if len(self._attach) != 0:
                tmpmsg = msg
                msg = MIMEMultipart()
                msg.attach(tmpmsg)

            for file_name, attachment_name in self._attach:
                # if not os.path.exists(file_name):
                if not self.validate_file_path(file_name):
                    logger.info("File '%s' does not exist.  Not attaching to email." % file_name)
                    continue
                # if not os.path.isfile(file_name):
                if not self.validate_file(file_name):
                    logger.info("Attachment '%s' is not a file.  Not attaching to email." % file_name)
                    continue
                # Guess at encoding type
                c_type, encoding = mimetypes.guess_type(file_name)
                if c_type is None or encoding is not None:
                    # No guess could be made so use a binary type.
                    c_type = 'application/octet-stream'
                maintype, subtype = c_type.split('/', 1)
                if maintype == 'text':
                    fp = open(file_name)
                    attach = MIMEText(fp.read(), _subtype=subtype)
                    fp.close()
                elif maintype == 'image':
                    fp = open(file_name, 'rb')
                    attach = MIMEImage(fp.read(), _subtype=subtype)
                    fp.close()
                elif maintype == 'audio':
                    fp = open(file_name, 'rb')
                    attach = MIMEAudio(fp.read(), _subtype=subtype)
                    fp.close()
                else:
                    fp = open(file_name, 'rb')
                    attach = MIMEBase(maintype, subtype)
                    attach.set_payload(fp.read())
                    fp.close()
                    # Encode the payload using Base64
                    encoders.encode_base64(attach)
                # Set the filename parameter
                if attachment_name is None:
                    filename = os.path.basename(file_name)
                else:
                    filename = attachment_name
                attach.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attach)

            # Add Image,
            if self._image_path:
                # This example assumes the image is in the current directory
                fp = open(self._image_path, 'rb')
                msg_image = MIMEImage(fp.read())
                fp.close()

                # Define the image's ID as referenced above
                msg_image.add_header('Content-ID', '<image1>')
                msg.attach(msg_image)

            # Some header stuff
            msg['Subject'] = self._subject
            msg['From'] = self._from
            msg['To'] = ", ".join(self._to)
            msg['CC'] = ", ".join(self._cc)
            msg.preamble = "You need a MIME enabled mail reader to see this message"

            # Send message
            msg = msg.as_string()
            server = smtplib.SMTP(self._smtp_server)
            server.sendmail(self._from, self._to + self._cc, msg)
            server.quit()
            logger.info("Successfully sent email(s) to {}".format(",".join(self._to)))
        except Exception as error:
            logger.error("Failed to send email(s) to {}".format(",".join(self._to)))
            logger.exception(error)


@display_arguments
def send_email(sender, recipients, subject, body, smtp_server=None, image_path=None,
               attachments=None, cc_recipients=None, body_type=None, alt_body=None):
    """
    Collects email components and sets up the email variables on email and sends out the email. If script is loaded from
    a non Production environment it will send emails     to Front Arena Support<frontarenasupport@nedbank.co.za>
    :param sender: Email Sender
    :type sender: str
    :param recipients: List of recipients to whom emails will be sent to.
    :type recipients: List[String]
    :param subject: String, Email Subject
    :type subject: str
    :param body: String/HTML String
    :param smtp_server: SMTP server. For Nedbank emails we use ''smtp.gmail.com', 587'
    :param image_path: String, If email body contains an image, the full path to the image is specified here.
    :param attachments: A list of full paths for all attachments to be included in the email.
    :rtype attachments: list[str]
    :param cc_recipients: List of recipients to Cc on email.
    :type cc_recipients: list[str]
    :param body_type: String, can be specified as 'html' or 'text'.
    :param alt_body: String, an Alternative email message should html text fail to load.
    :return: None
    """

    if not smtp_server:
        # 'smtp.gmail.com', 587
        smtp_server = 'smtp.gmail.com'
    message = CustomEmailService(smtp_server)
    if IS_PRODUCTION:
        for r_email in recipients:
            message.add_recipient(r_email.lower())
        for r_email in cc_recipients:
            message.add_cc_recipient(r_email.lower())
    else:
        subject = subject + " - Environment: {}".format("PRODUCTION")
        logger.info('This is not a PRODUCTION environment. No Email Sent')
        message.add_recipient("FrontArenaSupport@Nedbank.co.za".lower())

    message.sender = sender.lower()
    message.subject = subject
    if body_type.lower() == "html":
        message.set_html_body(body)
        message.set_text_body(alt_body)
    else:
        message.set_text_body(body)
    if image_path:
        message.set_image_path(image_path)
    for attachment_path in attachments:
        message.add_attachment(attachment_path)
    message.send()


if __name__ == "__main__":
    """
    This will send test emails and shows example of how the CustomEmailService class may be utilise to ease up 
    sending emails.
    If this python module is run in FRONT ARENA the __name__ is set to module name instead of '__main__' for 
    both import and reload/run. Hence, you cannot run this module in FRONT and expect test emails to be sent out 
    """



    # Run some tests
    m_from = "Gascoigne Nkambule <ncedison@nedbank.co.za>"
    m_to = "ncedison@nedbank.co.za"
    m = CustomEmailService("smtp.it.nednet.co.za")
    # m = Email("mail.mydomain.com")
    m.sender = m_from
    m.add_recipient(m_to)
    # m.add_recipient("ncediso@gmail.com")
    m.add_cc_recipient("ncediso@gmail.com")

    # Simple Plain Text Email
    m.subject = "Equity Client Valuation - Plain text email"
    m.set_text_body("This is a plain text email <b>I should not be bold</b>")
    m.send()

    # Plain text + attachment
    m.subject = "Equity Client Valuation - Text plus attachment"
    m.add_attachment(r"D:\Apps\Arena\nedcm_input\Attachments", "test.jpg")
    m.send()

    # Simple HTML Email
    m.clear_attachments()
    m.subject = "Equity Client Valuation - HTML Email"
    m.set_text_body(None)
    m.set_html_body("The following should be <b>bold</b>")
    m.send()

    # HTML + attachment
    m.subject = "Equity Client Valuation - HTML plus attachment"
    m.add_attachment(r"D:\Apps\Arena\nedcm_input\Attachments\test.xlsx")
    m.send()

    # Text + HTML
    m.clear_attachments()
    m.subject = "Equity Client Valuation - Text and HTML Message"
    m.set_text_body("You should not see this text in a MIME aware reader")
    m.send()

    # Text + HTML + attachment
    m.subject = "Equity Client Valuation - HTML + Text + attachment"
    html_text = '''
        <p> Hi Valued Client,</p>
        </br>
        <div style="background:green; color:white; padding:0">
            <h1>Client Valuation Report</h1>
        </div>

        <p><b>Some <i>HTML</i> text</b> and an image.</p>
        </br>
        <img src="cid:image1">
        </br>
        </br>
        Kind Regards,</br>
        Ncediso!
        '''
    m.set_text_body("I am looking at this Line")
    m.set_html_body(html_text)
    m.set_image_path(r"D:\Apps\Arena\nedcm_input\Attachments\test.jpg")
    m.add_attachment(r"D:\Apps\Arena\nedcm_input\Attachments", "test.pdf")
    m.send()

    # now you can play with your code. Let’s define the SMTP server separately here:
    port = 2525
    smtp_server = "smtp.mailtrap.io"
    login = "1a2b3c4d5e6f7g"  # paste your login generated by Mailtrap
    password = "1a2b3c4d5e6f7g"  # paste your password generated by Mailtrap

    # specify the sender’s and receiver’s email addresses
    sender = "from@example.com"
    receiver = "mailtrap@example.com"
