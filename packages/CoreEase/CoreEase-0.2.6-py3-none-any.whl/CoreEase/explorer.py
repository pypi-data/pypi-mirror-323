import os
def Rename(oldname,newname):
    os.rename(oldname,newname)
def CheckFileExistence(file):
    if os.path.exists(file):
        return True
    else:
        return None
def CreateFile(file):
    explorer = open(file, "w")
    explorer.write("")
    explorer.close()
def DeleteFile(file):
    os.remove(file)
def ReadFile(file):
    explorer = open(file, "r")
    content = explorer.read()
    explorer.close()
    return content
def AppendtoFile(file,content):
    explorer = open(file, "a")
    explorer.write(content + "\n")
    explorer.close()
def OverwriteFile(file,content):
    explorer = open(file, "w")
    explorer.write(content + "\n")
    explorer.close()
def CurrentDirectory():
    directory = os.getcwd()
    return directory
def ChangeDirectory(path):
    os.chdir(path)
def ListAllinDirectory():
    all = os.listdir(".")
    return all
def CreateDirectory(directory):
    os.mkdir(directory)
def CreateDirectoryStructure(directorystructure):
    os.makedirs(directorystructure, exist_ok=True)
def DeleteDirectory(directory):
    os.rmdir(directory)  
def DeleteDirectory(directorystructure):
    os.removedirs(directorystructure)