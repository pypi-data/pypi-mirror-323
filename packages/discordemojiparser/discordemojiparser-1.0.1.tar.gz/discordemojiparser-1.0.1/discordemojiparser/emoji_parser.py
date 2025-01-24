"""
Provides utilities for parsing and accessing Discord emojis.

Classes:
- EmojiParser: Utility class for parsing and managing Discord emojis.

Author:
DJ Stomp <85457381+DJStompZone@users.noreply.github.com>

License: MIT
Copyright 2025 Dylan Magar ("DJ Stomp")

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  A) The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  B) THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import re
from enum import EnumType
from typing import List, Dict, Optional
from discordemojiparser.emoji_enum import EmojiEnum


class EmojiParser:
    """
    A utility class for parsing and managing Discord emojis.

    This class provides methods to detect, validate, and extract emojis from text, 
    as well as generate URLs for Discord CDN-hosted emojis.

    Attributes:
        DISC_CDN (str): Base URL for Discord emoji assets.
        EMOJI_TEMPLATE (re.Pattern): Regex pattern for matching individual emojis.
        EMOJI_PATTERN (re.Pattern): Regex pattern for detecting emojis in text.
    """

    DISC_CDN: str = "https://cdn.discordapp.com/emojis"
    EMOJI_TEMPLATE: re.Pattern = re.compile(r"<:(a:)?(.+?):(\d+)>")
    EMOJI_PATTERN: re.Pattern = re.compile(r"<:.+?:\d+>")
    
    class Emoji:
        """
        Represents a Discord emoji.

        Attributes:
            name (str): The name of the emoji.
            snowflake (str): The unique ID of the emoji.
            anim (bool): Whether the emoji is animated.
            url (str): The URL to the emoji's image.
        """
        def __init__(self, match: re.Match):
            self.anim: bool = bool(match.group(1))
            self.name: str = match.group(2)
            self.snowflake: str = match.group(3)
            self.url: str = self.make_url()

        def make_url(self) -> str:
            """Generate the URL for the emoji's image."""
            extension = "gif" if self.anim else "png"
            return f"{EmojiParser.DISC_CDN}/{self.snowflake}.{extension}"

        def __repr__(self) -> str:
            return f"Emoji(name={self.name}, url={self.url})"

    @staticmethod
    def has_emoji(text: str) -> bool:
        """
        Check if the input text contains at least one emoji.

        Args:
            text (str): The input text to check.

        Returns:
            bool: True if the text contains at least one emoji, False otherwise.
        """
        return bool(re.search(EmojiParser.EMOJI_PATTERN, text))

    @staticmethod
    def is_emoji(text: str) -> bool:
        """
        Check if the input text is a valid single emoji.

        Args:
            text (str): The input text to validate.

        Returns:
            bool: True if the text is a valid emoji, False otherwise.
        """
        return bool(re.match(EmojiParser.EMOJI_TEMPLATE, text))

    @staticmethod
    def parse_single(emoji: str) -> Optional["EmojiParser.Emoji"]:
        """
        Parse a single emoji into an Emoji object.

        Args:
            emoji (str): The emoji string to parse.

        Returns:
            Optional[EmojiParser.Emoji]: The parsed Emoji object, or None if invalid.
        """
        match = re.match(EmojiParser.EMOJI_TEMPLATE, emoji)
        if match:
            return EmojiParser.Emoji(match)
        raise ValueError(f"Invalid emoji: {emoji}")

    @staticmethod
    def parse_all(text: str) -> List["EmojiParser.Emoji"]:
        """
        Parse all emojis in the input text into Emoji objects.

        Args:
            text (str): The text containing emojis.

        Returns:
            List[EmojiParser.Emoji]: A list of Emoji objects parsed from the text.
        """
        matches = re.finditer(EmojiParser.EMOJI_TEMPLATE, text)
        return [EmojiParser.Emoji(match) for match in matches]

    @staticmethod
    def get_emojis_json(text: str) -> Dict[str, str]:
        """
        Get a dictionary of emoji names and their URLs.

        Args:
            text (str): The text containing emojis.

        Returns:
            Dict[str, str]: A dictionary mapping emoji names to their URLs.
        """
        emojis = EmojiParser.parse_all(text)
        return {emoji.name: emoji.url for emoji in emojis}

    @staticmethod
    def get_emojis_enum(text: str, name="Emojis") -> EnumType:
        """
        Get an enum of Emoji objects

        Args:
            text (str): The text containing emojis.
            name (str): The name for the enum. (Default: "Emojis")

        Returns:
            EmojiEnum: An Enum of Emoji objects
        """
        emojis = EmojiParser.parse_all(text)
        return EmojiEnum(name, {emoji.name: emoji for emoji in emojis})
