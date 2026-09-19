### "getch" Module for BootysWordle

from platform import system as getos
from typing import Callable

def empty() -> None: ...
type EventHandler = Callable[[], None]
class GetchNotSupported(Exception): ...

match getos():

    case "Windows":

        from msvcrt import getwch as _getwch

        def getch() -> str:
            char = _getwch()
            return (
                char if char not in {"\xe0", "\x00"}
                else char + _getwch()
            )

        class Key:
            DOWN = "\xe0P"
            UP = "\xe0H"
            LEFT = "\xe0K"
            RIGHT = "\xe0M"
            ENTER = "\r"
            BACKSPACE = "\b"
            _CTRL_C = "\x03"

    case "Linux" | "Darwin":

        from sys import stdin
        from termios import tcgetattr, tcsetattr, TCSADRAIN
        from tty import setcbreak

        def getch() -> str:
            fd = stdin.fileno()
            attrs = tcgetattr(fd)
            try:
                setcbreak(fd)
                char = stdin.read(1)
                if char != "\x1b": # Assume user didn't press ESC
                    return char
                char2 = stdin.read(1)
                return (
                    char if char2 != "["
                    else char + char2 + stdin.read(1)
                )
            finally:
                tcsetattr(fd, TCSADRAIN, attrs)

        class Key:
            DOWN = "\x1b[B"
            UP = "\x1b[A"
            LEFT = "\x1b[D"
            RIGHT = "\x1b[C"
            ENTER = "\n"
            BACKSPACE = "\b"
            _CTRL_C = None

    case _:

        raise GetchNotSupported(f"getch() not supported on OS: {getos()}")

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def input5(val: str = "", *, indent: int = 0) -> str:
    """Gets a 5 character long input"""

    result = val
    print(
        f"\r\x1b[{indent}C",
        *[f"\x1b[30m[\x1b[39m{ch.upper()}\x1b[30m]\x1b[39m" for ch in result.ljust(5)],
        f"\r\x1b[{1 + len(result) * 3 + indent}C",
        sep="",
        end="",
        flush=True
    )

    while True:
        char = getch().lower()
    
        match char:
            case Key.ENTER:
                if len(result) < 5:
                    continue
                print()
                break

            case Key.BACKSPACE:
                if len(result) == 0:
                    continue
                result = result[:-1]
                print(
                    f"\x1b[1E\x1b[0K\x1b[1F\x1b[{indent}C",
                    *[f"\x1b[30m[\x1b[39m{ch.upper()}\x1b[30m]\x1b[39m" for ch in result.ljust(5)],
                    f"\r\x1b[{1 + len(result) * 3 + indent}C",
                    sep="",
                    end="",
                    flush=True
                )

            case Key._CTRL_C:
                raise KeyboardInterrupt
            
            case _:
                if char not in ALPHABET \
                    or len(result) == 5:
                    continue
                result += char
                print(
                    f"\r\x1b[{indent}C",
                    *[f"\x1b[30m[\x1b[39m{ch.upper()}\x1b[30m]\x1b[39m" for ch in result.ljust(5)],
                    f"\r\x1b[{1 + len(result) * 3 + indent}C",
                    sep="",
                    end="",
                    flush=True
                )

    return result
