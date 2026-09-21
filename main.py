### BootysWordle / main.py

# Imports

from base64 import b64encode, b64decode
from pathlib import Path
from random import randint as randint
from typing import Literal
from modules.getch import input5
from enum import Enum

# Consts

ROOT = Path(__file__).parent
VLD_FILE = ROOT / "assets" / "VLD"
SLN_FILE = ROOT / "assets" / "SLN"

VLD_LEN = 10657
SLN_LEN = 2315
MAX_TRIES = 6

# Types

type b64str = str
type checkint = Literal[0, 1, 2]
type checktuple = tuple[checkint, checkint, checkint, checkint, checkint]

class PlayState(Enum):
    INIT = 0
    WIN = 1
    LOSE = 2
    EXIT = 3

# Functions

def encode(s: str) -> b64str:
    return b64encode(s.encode()).decode()

def decode(s: b64str) -> str:
    return b64decode(s.encode()).decode()

def isvalid(word: str) -> bool:
    return encode(word) in VLD_FILE.read_text() \
        or encode(word) in SLN_FILE.read_text()

def check(word: str, sln: str) -> checktuple:
    checked = [0] * 5
    chars = []

    for i in range(5):
        ch = word[i]
        if ch == sln[i]:
            checked[i] = 2
            chars.append(ch)
    
    for i in range(5):
        ch = word[i]
        if ch in sln \
            and checked[i] != 2 \
            and chars.count(ch) < sln.count(ch):
            checked[i] = 1
            chars.append(ch)

    return tuple(checked)

def color(word: str, checked: checktuple) -> str:
    colors = [
        "\x1b[30m",
        "\x1b[33m",
        "\x1b[32m"
    ]

    return "".join([f"{colors[checked[i]]}[{word[i].upper()}]\x1b[39m" for i in range(5)])

def randsln() -> str:
    with open(SLN_FILE) as f:
        i = randint(1, SLN_LEN) * 8
        return decode(f.read().replace("\n", "")[i - 8:i])

# Main

def play() -> tuple[str, PlayState]:
    SOLUTION = randsln()

    for i in range(MAX_TRIES):
        word = ""

        while True:
            print(f"\n\x1b[1F\x1b[30m{i + 1}/{MAX_TRIES}\x1b[39m", end="", flush=True)
            try:
                word = input5(word, indent=4)
            except KeyboardInterrupt:
                print("\n\x1b[0K", end="", flush=True)
                return SOLUTION, PlayState.EXIT

            if not isvalid(word):
                print("\x1b[31m[!] INVALID\x1b[39m\x1b[1F", end="", flush=True)
            else:
                print("\x1b[0K", end="", flush=True)
                break

        checked = check(word, SOLUTION)
        print(
            f"\x1b[1F\x1b[30m{i + 1}/{MAX_TRIES}\x1b[39m",
            color(word, checked),
            "".join((
                f"\x1b[30m{checked.count(0)}",
                f"\x1b[33m{checked.count(1)}",
                f"\x1b[32m{checked.count(2)}",
                "\x1b[39m"
            ))
        )
        if word == SOLUTION:
            return SOLUTION, PlayState.WIN
    
    return SOLUTION, PlayState.LOSE

def main():
    state = PlayState.INIT
    i = 0
    print()

    # Loop until player presses Ctrl + C
    while state is not PlayState.EXIT:
        i += 1
        print(f"\n\x1b[30m====[[ ROUND_{i:03} ]]====\x1b[39m\n")
        sln, state = play()

        if state is PlayState.WIN:
            continue

        # Player either exited or lost
        i = 0
        print(
            "\n\x1b[30m====[[ GAME_OVER ]]====",
            "\x1b[31m",
            f"    {''.join([f'[{ch.upper()}]' for ch in sln])}    ",
            "\x1b[39m",
            sep="\n",
            end="\n\n" if state is PlayState.EXIT else "\n"
        )

if __name__ == "__main__":
    main()