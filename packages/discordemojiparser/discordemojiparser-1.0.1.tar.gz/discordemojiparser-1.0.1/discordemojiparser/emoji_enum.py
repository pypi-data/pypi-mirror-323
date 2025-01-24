"""
Provides utilities for parsing and accessing Discord emojis.

Classes:
- EmojiEnumMeta: Custom metaclass to override attribute access for emoji values.
- EmojiEnum: Custom Enum for storing Emoji objects.

Author:
DJ Stomp <85457381+DJStompZone@users.noreply.github.com>

License: MIT
Copyright 2025 Dylan Magar ("DJ Stomp")

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  A) The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  B) THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from enum import Enum, EnumMeta

class EmojiEnumMeta(EnumMeta):
    """Custom EnumMeta to override attribute access for emoji values."""

    def __getitem__(self, item: str):
        """Enable dictionary-style access to enum members."""
        member = super().__getitem__(item)
        return member.value

    def __getattr__(self, name: str):
        """Allow direct attribute access to the Emoji objects' attributes."""
        member = self.__members__.get(name)
        if member:
            return member.value
        raise AttributeError(f"{self.__name__} has no attribute {name}")


class EmojiEnum(Enum, metaclass=EmojiEnumMeta):
    """Custom Enum for storing Emoji objects."""
    def __init__(self, *args, **kwargs):
        # Prevent any special init behavior from interfering
        pass

