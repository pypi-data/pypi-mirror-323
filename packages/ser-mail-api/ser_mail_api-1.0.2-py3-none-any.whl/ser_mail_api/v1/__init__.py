"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from .client import Client
from .data import *

__all__ = ['Client', 'Attachment','FileAttachment', 'StreamAttachment', 'Disposition', 'Content', 'ContentType', 'MailUser', 'Message']
