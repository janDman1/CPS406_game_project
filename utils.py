import re
import sys
from time import sleep

type objUID = str

def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)

def delay(speed_number=2) -> None:
    sys.stdout.flush()
    match speed_number:
        case 0:
            pass
        case 1:
            sleep(0.3)
        case 2:
            sleep(1.2)
        case 3:
            sleep(2.3)
        case 4:
            sleep(4)
        case 5:
            sleep(7)

def symsymsym(symbol: str, newline=True) -> None:
    delay()
    for _ in range(3):
        print(f"{symbol}", end="")
        delay(1)
    if newline:
        print()

def dotdotdot(newline=True) -> None:
    symsymsym(".", newline)

