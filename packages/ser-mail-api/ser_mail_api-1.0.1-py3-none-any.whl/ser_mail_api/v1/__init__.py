"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from .client import Client
from .data.attachment import Attachment, FileAttachment, StreamAttachment, Disposition
from .data.content import Content, ContentType
from .data.mailuser import MailUser
from .data.message import Message

__all__ = ['Client', 'Attachment','FileAttachment', 'StreamAttachment', 'Disposition', 'Content', 'ContentType', 'MailUser', 'Message']
