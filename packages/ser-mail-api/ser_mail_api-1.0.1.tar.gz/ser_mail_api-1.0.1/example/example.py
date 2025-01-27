import json

from ser_mail_api.v1 import *

if __name__ == "__main__":
    # Load API key
    with open("../ser.api_key", "r") as api_key_file:
        api_key_data = json.load(api_key_file)

    client = Client(api_key_data.get("client_id"), api_key_data.get("client_secret"))

    # Create a new Message object
    message = Message("This is a test email", MailUser("sender@proofpoint.com", "Joe Sender"))
    # Add content body
    message.add_content(Content("This is a test message", ContentType.TEXT))
    message.add_content(Content("<b>This is a test message</b>", ContentType.HTML))
    # Add Recipients
    message.add_recipient(MailUser("recipient1@proofpoint.com", "Recipient 1"))
    message.add_recipient(MailUser("recipient2@proofpoint.com", "Recipient 2"))
    # Add CC
    message.add_cc(MailUser("cc1@proofpoint.com", "Carbon Copy 1"))
    message.add_cc(MailUser("cc2@proofpoint.com", "Carbon Copy 2"))
    # Add BCC
    message.add_bcc(MailUser("bcc1@proofpoint.com", "Blind Carbon Copy 1"))
    message.add_bcc(MailUser("bcc2@proofpoint.com", "Blind Carbon Copy 2"))

    # Add Base64 Encoded Attachment
    message.add_attachment(Attachment("VGhpcyBpcyBhIHRlc3Qh", Disposition.ATTACHMENT, "test.txt", "text/plain"))

    # Add File Attachment from Disk, if Disposition is not passed, the default is Disposition.ATTACHMENT
    message.add_attachment(FileAttachment(r"C:\temp\file.csv", Disposition.ATTACHMENT))

    # In the following example, we will create a byte stream from a string. This byte stream is converted
    # to base64 encoding within the StreamAttachment object
    text = "This is a sample text stream."

    # Convert the string into bytes
    byte_stream = text.encode("utf-8")

    # Add Byte Stream as Attachment, if Disposition is not passed, the default is Disposition.ATTACHMENT
    message.add_attachment(StreamAttachment(byte_stream,"byte_stream.txt", "text/plain", Disposition.ATTACHMENT))

    result = client.send(message)

    print("HTTP Status", result.get_status())
    print("HTTP Reason", result.get_reason())

    print("Reason:", result.reason)
    print("Message ID:", result.message_id)
    print("Request ID:", result.request_id)
