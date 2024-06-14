from typing import List
import re


def parse_bulleted_list(text: str) -> List[str]:
    return re.findall("(?:^|\n)- ([^\n]+)", text)
