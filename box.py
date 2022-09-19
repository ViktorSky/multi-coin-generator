# made by V¡ktor
# 2022-09-06
# thanks for using box.py <3

import os
from datetime import datetime
from random import choice
from string import (
    ascii_letters,
    digits
)

from pytz import timezone


clear = lambda: os.system("cls" if os.name == "nt" else "clear")


def tzFilter(hour: int = 23, tz: str = None) -> int:
    # Examples:
    # >> tzFilter(hour = 18)
    # -300
    #
    # >> tzFilter(tz = "Etc/GMT+5")
    # -300
    zones = ['Etc/GMT' + (f'+{i}' if i > 0 else f'{i}') for i in range(-12, 12)]
    
    return next(int(
            datetime.now(timezone(_)).strftime("%Z").replace("GMT", "00")
        ) * 60 for _ in ([tz] if tz else zones) if (
            tz or (int(datetime.now(timezone(_)).strftime("%H")) == hour)
        )
    )



def randomCode(length: int = 15, chars: (str, list, tuple) = None) -> str:
    # Example:
    # >> randomCode(length = 8, chars = "aeiou12345")
    # '552ei4o4'
    return "".join(choice(
            list(chars) if chars else list(ascii_letters + digits + "!@#$%&")
        ) for _ in range(length)
    )

