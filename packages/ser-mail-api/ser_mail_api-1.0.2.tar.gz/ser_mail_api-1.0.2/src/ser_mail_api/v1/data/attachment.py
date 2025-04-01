import base64
import mimetypes
import os
import uuid
from enum import Enum
from typing import Dict, Optional


def _is_valid_base64(s: str) -> bool:
    """Check if a string is valid Base64."""
    try:
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False


class Disposition(Enum):
    INLINE = "inline"
    ATTACHMENT = "attachment"


class Attachment:
    def __init__(self, content: str, disposition: Disposition, filename: str, mime_type: str):
        # Validate input types
        if not isinstance(content, str):
            raise TypeError(f"Expected 'content' to be a string, got {type(content).__name__}")
        if not isinstance(disposition, Disposition):
            raise TypeError(f"Expected 'disposition' to be a Disposition, got {type(disposition).__name__}")
        if not isinstance(filename, str):
            raise TypeError(f"Expected 'filename' to be a string, got {type(filename).__name__}")
        if not isinstance(mime_type, str):
            raise TypeError(f"Expected 'mime_type' to be a string, got {type(mime_type).__name__}")

        # Validate specific constraints
        if not _is_valid_base64(content):
            raise ValueError("Invalid Base64 content")
        if len(filename) > 1000:
            raise ValueError("Filename must be at most 1000 characters long")
        if not mime_type.strip():
            raise ValueError("Mime type must be a non-empty string")

        # Set attributes
        self.__id = str(uuid.uuid4())
        self.__content = content
        self.__disposition = disposition
        self.__filename = filename
        self.__mime_type = mime_type

    @property
    def id(self) -> str:
        return self.__id

    @property
    def content(self) -> str:
        return self.__content

    @property
    def disposition(self) -> Disposition:
        return self.__disposition

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def mime_type(self) -> str:
        return self.__mime_type

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "disposition": self.disposition.value,
            "filename": self.filename,
            "id": self.id,
            "type": self.mime_type,
        }

    def __repr__(self) -> str:
        return (
            f"Attachment(id={self.__id!r}, filename={self.__filename!r}, "
            f"disposition={self.__disposition.value!r}, mime_type={self.__mime_type!r})"
        )


class FileAttachment(Attachment):
    def __init__(self, file_path: str, disposition: Disposition = Disposition.ATTACHMENT, mime_type: Optional[str] = None):
        """
        Args:
            file_path (str): Path to the file.
            disposition (Disposition): The disposition of the attachment (inline or attachment).
            mime_type (Optional[str]): The MIME type of the file. If None, it will be deduced from the file path.
        """
        if not isinstance(file_path, str):
            raise TypeError(f"Expected 'file_path' to be a string, got {type(file_path).__name__}")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file at path '{file_path}' does not exist.")

        # Use provided mime_type or deduce it
        if mime_type is None:
            mime_type = self._deduce_mime_type(file_path)

        # Encode file content
        content = self._encode_file_content(file_path)
        filename = os.path.basename(file_path)

        super().__init__(content, disposition, filename, mime_type)

    @staticmethod
    def _deduce_mime_type(file_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            raise ValueError(f"Unable to deduce MIME type for file: {file_path}")
        return mime_type

    @staticmethod
    def _encode_file_content(file_path: str) -> str:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")


class StreamAttachment(Attachment):
    def __init__(self, stream: bytes, filename: str, mime_type: str, disposition: Disposition = Disposition.ATTACHMENT):
        """
        Args:
            stream (bytes): Byte stream of the content.
            filename (str): Filename of the attachment.
            mime_type (str): MIME type of the content.
            disposition (Disposition): The disposition of the attachment (inline or attachment).
        """
        if not isinstance(stream, bytes):
            raise TypeError(f"Expected 'stream' to be bytes, got {type(stream).__name__}")
        if not isinstance(filename, str):
            raise TypeError(f"Expected 'filename' to be a string, got {type(filename).__name__}")
        if not isinstance(mime_type, str):
            raise TypeError(f"Expected 'mime_type' to be a string, got {type(mime_type).__name__}")

        # Encode stream to Base64
        content = base64.b64encode(stream).decode("utf-8")

        super().__init__(content, disposition, filename, mime_type)
