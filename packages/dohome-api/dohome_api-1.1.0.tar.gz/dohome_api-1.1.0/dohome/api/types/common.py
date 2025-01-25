"""DoIT API common types"""
from typing import TypedDict

# DoInt represents positive value between 0 and 5000
DoInt = int

# DoRGB represents RGB color
DoRGB = tuple[DoInt, DoInt, DoInt]

# DoWhite represents white temperature.
# Values should be 5000 in sum. Yellow first, blue second
DoWhite = tuple[DoInt, DoInt]

# DoTime represents time
DoTime = TypedDict("DoTime", {
    "year": int, # e.g. 2022
    "month": int, # e.g. 1
    "day": int, # e.g. 27
    "hour": int, # e.g. 15
    "minute": int, # e.g. 45
    "second": int # e.g. 57
})

BaseRequest = TypedDict("BaseRequest", {
    "cmd": int
})

BaseResponse = TypedDict("BaseResponse", {
    "cmd": int,
    "res": int,
})
