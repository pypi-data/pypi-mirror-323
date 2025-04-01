# Proofpoint Secure Email Relay Mail API Package

[![PyPI Downloads](https://static.pepy.tech/badge/ser-mail-api)](https://pepy.tech/projects/ser-mail-api)  
Library implements all the functions of the SER Email Relay User Management API via Python.

### Requirements:

* Python 3.9+
* requests
* requests-oauth2client
* pysocks

### Installing the Package

You can install the tool using the following command directly from Github.

```
pip install git+https://github.com/pfptcommunity/ser-mail-api-python.git
```

or can install the tool using pip.

```
# When testing on Ubuntu 24.04 the following will not work:
pip install ser-mail-api
```

If you see an error similar to the following:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

You should use install pipx or you can configure your own virtual environment and use the command referenced above.

```
pipx install ser-mail-api
```

### Creating an API client object

```python
from ser_mail_api.v1 import *

if __name__ == "__main__":
    client = Client("<client_id>", "<client_secret>")
```

### Sending an Email Message

```python
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
    message.add_attachment(StreamAttachment(byte_stream, "byte_stream.txt", "text/plain", Disposition.ATTACHMENT))

    result = client.send(message)

    print("HTTP Status", result.get_status())
    print("HTTP Reason", result.get_reason())

    print("Reason:", result.reason)
    print("Message ID:", result.message_id)
    print("Request ID:", result.request_id)
```

The following JSON data is a dump of the message object based on the code above.

```json
{
  "attachments": [
    {
      "content": "VGhpcyBpcyBhIHRlc3Qh",
      "disposition": "attachment",
      "filename": "test.txt",
      "id": "d10205cf-a0a3-4b9e-9a57-253fd8e1c7df",
      "type": "text/plain"
    },
    {
      "content": "77u/IlVzZXIiLCJTZW50Q291bnQiLCJSZWNlaXZlZENvdW50Ig0KIm5vcmVwbHlAcHJvb2Zwb2ludC5jb20sIGxqZXJhYmVrQHBmcHQuaW8iLCIwIiwiMCINCg==",
      "disposition": "attachment",
      "filename": "file.csv",
      "id": "f66487f5-57c2-40e0-9402-5723a85c0df0",
      "type": "application/vnd.ms-excel"
    },
    {
      "content": "VGhpcyBpcyBhIHNhbXBsZSB0ZXh0IHN0cmVhbS4=",
      "disposition": "attachment",
      "filename": "byte_stream.txt",
      "id": "bc67d5fa-345a-4436-9979-5efa68223520",
      "type": "text/plain"
    }
  ],
  "content": [
    {
      "body": "This is a test message",
      "type": "text/plain"
    },
    {
      "body": "<b>This is a test message</b>",
      "type": "text/html"
    }
  ],
  "from": {
    "email": "sender@proofpoint.com",
    "name": "Joe Sender"
  },
  "headers": {
    "from": {
      "email": "sender@proofpoint.com",
      "name": "Joe Sender"
    }
  },
  "subject": "This is a test email",
  "tos": [
    {
      "email": "recipient1@proofpoint.com",
      "name": "Recipient 1"
    },
    {
      "email": "recipient2@proofpoint.com",
      "name": "Recipient 2"
    }
  ],
  "cc": [
    {
      "email": "cc1@proofpoint.com",
      "name": "Carbon Copy 1"
    },
    {
      "email": "cc2@proofpoint.com",
      "name": "Carbon Copy 2"
    }
  ],
  "bcc": [
    {
      "email": "bcc1@proofpoint.com",
      "name": "Blind Carbon Copy 1"
    },
    {
      "email": "bcc2@proofpoint.com",
      "name": "Blind Carbon Copy 2"
    }
  ],
  "replyTos": []
}
```

### Proxy Support

Socks5 Proxy Example:

```python
from ser_mail_api.v1 import *

if __name__ == '__main__':
    client = Client("<client_id>", "<client_secret>")
    credentials = "{}:{}@".format("proxyuser", "proxypass")
    client._session.proxies = {'https': "{}://{}{}:{}".format('socks5', credentials, '<your_proxy>', '8128')}
```

HTTP Proxy Example (Squid):

```python
from ser_mail_api.v1 import *

if __name__ == '__main__':
    client = Client("<client_id>", "<client_secret>")
    credentials = "{}:{}@".format("proxyuser", "proxypass")
    client._session.proxies = {'https': "{}://{}{}:{}".format('http', credentials, '<your_proxy>', '3128')}

```

### HTTP Timeout Settings

```python
from ser_mail_api.v1 import *

if __name__ == '__main__':
    client = Client("<client_id>", "<client_secret>")
    # Timeout in seconds, connect timeout
    client.timeout = 600
    # Timeout advanced, connect / read timeout
    client.timeout = (3.05, 27)
```

### Limitations

There are no known limitations.

For more information please see: https://api-docs.ser.proofpoint.com/docs/email-submission
