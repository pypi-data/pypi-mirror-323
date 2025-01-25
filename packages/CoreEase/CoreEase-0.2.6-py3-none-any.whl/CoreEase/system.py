import os
import shutil
import datetime
def Shutdown():
    os.system("shutdown /s /t 10")
def Restart():
    os.system("shutdown /r /t 10")
def CPUCount():
    cpucount = os.cpu_count()
    return cpucount
def ConsoleHeight():
    consoleheight = shutil.get_terminal_size().lines
    return consoleheight
def ConsoleWidth():
    consolewidth = shutil.get_terminal_size().columns
    return consolewidth
def CurrentSystemTime():
    time = datetime.datetime.now()
    return time
def GetEnvironmentVariable(key):
    value = os.environ.get(key)
    return value
def GetAllEnvironmentVariables():
    variablelist = []
    userprofile = os.environ.get('USERPROFILE')
    appdata = os.environ.get('APPDATA')
    localappdata = os.environ.get('LOCALAPPDATA')
    temp = os.environ.get('TEMP')
    path = os.environ.get('PATH')
    homedrive = os.environ.get('HOMEDRIVE')
    homepath = os.environ.get('HOMEPATH')
    programfiles = os.environ.get('PROGRAMFILES')
    programfiles_x86 = os.environ.get('PROGRAMFILES(X86)')
    systemroot = os.environ.get('SYSTEMROOT')
    comspec = os.environ.get('COMSPEC')
    logname = os.environ.get('LOGNAME')
    computername = os.environ.get('COMPUTERNAME')
    processor_identifier = os.environ.get('PROCESSOR_IDENTIFIER')
    systemdrive = os.environ.get('SYSTEMDRIVE')
    windir = os.environ.get('WINDIR')
    currentos = os.environ.get('OS')
    userdomain = os.environ.get('USERDOMAIN')
    username = os.environ.get('USERNAME')
    prompt = os.environ.get('PROMPT')
    sessionname = os.environ.get('SESSIONNAME')
    logonserver = os.environ.get('LOGONSERVER')
    variablelist.append(userprofile)
    variablelist.append(appdata)
    variablelist.append(localappdata)
    variablelist.append(temp)
    variablelist.append(path)
    variablelist.append(homedrive)
    variablelist.append(homepath)
    variablelist.append(programfiles)
    variablelist.append(programfiles_x86)
    variablelist.append(systemroot)
    variablelist.append(comspec)
    variablelist.append(logname)
    variablelist.append(computername)
    variablelist.append(processor_identifier)
    variablelist.append(systemdrive)
    variablelist.append(windir)
    variablelist.append(currentos)
    variablelist.append(userdomain)
    variablelist.append(username)
    variablelist.append(prompt)
    variablelist.append(sessionname)
    variablelist.append(logonserver)
    return variablelist