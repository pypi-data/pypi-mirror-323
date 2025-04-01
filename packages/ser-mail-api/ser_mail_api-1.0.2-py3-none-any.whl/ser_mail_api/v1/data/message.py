import json
from typing import List, Dict

from .attachment import Attachment
from .content import Content
from .mailuser import MailUser


class Message:
    def __init__(self, subject: str, sender: MailUser):
        if not isinstance(sender, MailUser):
            raise TypeError(f"Expected sender to be a MailUser, got {type(sender).__name__}")
        if not isinstance(subject, str):
            raise TypeError(f"Expected subject to be a string, got {type(subject).__name__}")

        self.__subject = subject
        self.__sender = sender
        self.__header_sender = sender
        self.__recipients: List[MailUser] = []
        self.__cc: List[MailUser] = []
        self.__bcc: List[MailUser] = []
        self.__reply_tos: List[MailUser] = []
        self.__attachments: List[Attachment] = []
        self.__content: List[Content] = []
        self.__headers: Dict[str, Dict] = {}

    @property
    def sender(self) -> MailUser:
        return self.__header_sender

    @sender.setter
    def sender(self, sender: MailUser):
        if not isinstance(sender, MailUser):
            raise TypeError(f"Expected sender to be a MailUser, got {type(sender).__name__}")
        self.__header_sender = sender

    @property
    def header_sender(self) -> MailUser:
        return self.__header_sender

    @header_sender.setter
    def header_sender(self, sender: MailUser):
        if not isinstance(sender, MailUser):
            raise TypeError(f"Expected header_sender to be a MailUser, got {type(sender).__name__}")
        self.__header_sender = sender

    def add_recipient(self, recipient: MailUser):
        if not isinstance(recipient, MailUser):
            raise TypeError(f"Expected recipient to be a MailUser, got {type(recipient).__name__}")
        self.__recipients.append(recipient)

    def add_cc(self, cc_user: MailUser):
        if not isinstance(cc_user, MailUser):
            raise TypeError(f"Expected cc_user to be a MailUser, got {type(cc_user).__name__}")
        self.__cc.append(cc_user)

    def add_bcc(self, bcc_user: MailUser):
        if not isinstance(bcc_user, MailUser):
            raise TypeError(f"Expected bcc_user to be a MailUser, got {type(bcc_user).__name__}")
        self.__bcc.append(bcc_user)

    def add_reply_to(self, reply_to_user: MailUser):
        if not isinstance(reply_to_user, MailUser):
            raise TypeError(f"Expected reply_to_user to be a MailUser, got {type(reply_to_user).__name__}")
        self.__reply_tos.append(reply_to_user)

    def add_attachment(self, attachment: Attachment):
        if not isinstance(attachment, Attachment):
            raise TypeError(f"Expected attachment to be an Attachment, got {type(attachment).__name__}")
        self.__attachments.append(attachment)

    def add_content(self, content: Content):
        if not isinstance(content, Content):
            raise TypeError(f"Expected content to be a Content, got {type(content).__name__}")
        self.__content.append(content)

    def set_header(self, key: str, value: Dict):
        if not isinstance(key, str):
            raise TypeError(f"Expected key to be a string, got {type(key).__name__}")
        if not isinstance(value, dict):
            raise TypeError(f"Expected value to be a dictionary, got {type(value).__name__}")
        self.__headers[key] = value

    def to_dict(self) -> Dict:
        """Convert the message to a dictionary suitable for JSON serialization."""
        return {
            "attachments": [attachment.to_dict() for attachment in self.__attachments],
            "content": [content.to_dict() for content in self.__content],
            "from": self.__sender.to_dict(),
            "headers": self.__headers or {"from": self.__header_sender.to_dict()},
            "subject": self.__subject,
            "tos": [recipient.to_dict() for recipient in self.__recipients],
            "cc": [cc_user.to_dict() for cc_user in self.__cc],
            "bcc": [bcc_user.to_dict() for bcc_user in self.__bcc],
            "replyTos": [reply_to_user.to_dict() for reply_to_user in self.__reply_tos],
        }

    def __str__(self) -> str:
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict(), indent=4)
