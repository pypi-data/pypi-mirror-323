import os
import math
from concurrent.futures import ThreadPoolExecutor
from .system import ConsoleWidth
executor = ThreadPoolExecutor(max_workers=4)
def SubmitTasktoThreadWITHLoadBuffer(task):
    future = executor.submit(task)
    LoadBuffer(future)
    return future.result()
def SubmitTasktoThreadWITHLoadBufferNOAnimation(task):
    future = executor.submit(task)
    LoadBufferNOAnimation(future)
    return future.result()
def SubmitTasktoThreadNOLoadBuffer(task):
    future = executor.submit(task)
    return future
def LoadBuffer(future):
    console_w = ConsoleWidth()
    console_parts = math.floor((console_w // 2) - 1.5)
    while future.done() != True:
        print(" " * console_parts + "--/" + " " * console_parts, end="\r")
        print(" " * console_parts + "---" + " " * console_parts, end="\r")
        print(" " * console_parts + "--\\" + " " * console_parts, end="\r")
        print(" " * console_parts + "--|" + " " * console_parts, end="\r")
    else:
        print(future)
def LoadBufferNOAnimation(future):
    while future.done() != True:
        pass
    else:
        print(future)
def PassCommandtoConsole(command):
    os.system(command)