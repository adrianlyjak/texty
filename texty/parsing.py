from typing import List
import re

from bs4 import Tag


def parse_bulleted_list(text: str) -> List[str]:
    return re.findall("(?:^|\n)- ([^\n]+)", text)
