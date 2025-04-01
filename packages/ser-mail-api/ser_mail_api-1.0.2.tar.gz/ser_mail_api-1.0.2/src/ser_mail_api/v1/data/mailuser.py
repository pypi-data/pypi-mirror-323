from __future__ import annotations

from typing import Dict, Optional


class MailUser:
    def __init__(self, email: str, name: Optional[str] = None):
        # Validate email and name types
        if not isinstance(email, str):
            raise TypeError(f"Expected 'email' to be a string, got {type(email).__name__}")
        if name is not None and not isinstance(name, str):
            raise TypeError(f"Expected 'name' to be a string or None, got {type(name).__name__}")

        # Set attributes (immutable after initialization)
        self.__email = email
        self.__name = name

    @property
    def email(self) -> str:
        """Get the email address."""
        return self.__email

    @property
    def name(self) -> Optional[str]:
        """Get the display name."""
        return self.__name

    def to_dict(self) -> Dict:
        """Convert the MailUser to a dictionary."""
        return {
            "email": self.__email,
            "name": self.__name,
        }

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"MailUser(email={self.__email!r}, name={self.__name!r})"
