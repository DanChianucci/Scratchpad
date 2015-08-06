#!/usr/bin/env python
"""
    Git filter to smudge various information into file headers.
"""

import sys
import os
import subprocess
import time
import re



################################################################################
###  REGEX
################################################################################
VER_REGEX       = re.compile(r"(\$Version:?)(.*)(\$)",flags=re.IGNORECASE)
FILE_REGEX      = re.compile(r"(\$File:?)(.*)(\$)",flags=re.IGNORECASE)
DATE_REGEX      = re.compile(r"(\$Date:?)(.*)(\$)",flags=re.IGNORECASE)
AUTHOR_REGEX    = re.compile(r"(\$Author:?)(.*)(\$)",flags=re.IGNORECASE)
ID_REGEX        = re.compile(r"(\$Id:?)(.*)(\$)",flags=re.IGNORECASE)
MSG_REGEX       = re.compile(r"(\$Message:?)(.*)(\$)",flags=re.IGNORECASE)



SMUDGE = "smudge"
CLEAN  = "clean"


################################################################################
###  Git Commands
################################################################################
def getBranchName():
    try:
        process = subprocess.Popen(["/usr/bin/git", "symbolic-ref", "HEAD"],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, err:
        return _error("Can't get git branch: %s" % err)
    process.wait()

    

    if process.returncode == 0:
        branchname = process.stdout.readline().strip().split('/')[-1]
    else:
        branchname = "(unamed branch)"

    return branchname

def getNumVersions(filename):
    try:
        process = subprocess.Popen(["/usr/bin/git", "log","--pretty=oneline","--", filename],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, err:
        return _error("Can't get version number for %s \n %s" % filename, err)
    process.wait()



    if process.returncode == 0:
        num_lines = sum(1 for line in process.stdout);
    else:
        num_lines = "(unknown version)"
    return num_lines

def getCommitAuthor(filename):
    try:
        process = subprocess.Popen(["/usr/bin/git", "log",'--pretty=format:%aN - <%aE>',"-1","--", filename],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, err:
        return _error("Can't get commit author for %s \n %s" % filename, err)
    process.wait()



    if process.returncode == 0:
        author = process.stdout.readline();
    else:
        author = "(Unknown Commit Author)"
    return author

def getCommitDate(filename):
    try:
        process = subprocess.Popen(["/usr/bin/git", "log",'--pretty=format:%cd',"-1","--", filename],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, err:
        return _error("Can't get commit date for %s \n %s" % filename, err)
    process.wait()



    if process.returncode == 0:
        date = process.stdout.readline();
    else:
        date = "(Unknown Commit Date)"
    return date

def getCommitId(filename):
    try:
        process = subprocess.Popen(["/usr/bin/git", "log",'--pretty=format:%H',"-1","--", filename],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, err:
        return _error("Can't get commit ID for %s \n %s" % filename, err)
    process.wait()

    if process.returncode == 0:
        ID = process.stdout.readline();
    else:
        ID = "(Unknown Commit Id)"
    return ID

def getCommitMessage(filename):
    try:
        process = subprocess.Popen(["/usr/bin/git", "log",'--pretty=format:%s',"-1","--", filename],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception, err:
        return _error("Can't get commit message for %s \n %s" % filename, err)
    process.wait()

    if process.returncode == 0:
        msg = process.stdout.readline();
    else:
        msg = "(Unknown Commit Messgae)"
    return msg


################################################################################
###  Main Functionality
################################################################################
def _error(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    sys.exit(1)

def re_smudge(line,repl,regex):
    return regex.sub("\\1\t"+str(repl)+" \\3",line)

def re_clean(line,regex):
    return regex.sub(r"\1\3",line)

def smudge(filename):
    branchname = getBranchName()
    numVersions = getNumVersions(filename)
    
    version_str = "%s:%s"%(branchname,numVersions)    
    author_str  = getCommitAuthor(filename)
    date_str    = getCommitDate(filename)
    id_str      = getCommitId(filename)
    msg_str     = getCommitMessage(filename)

    for line in sys.stdin:
        line = re_smudge(line,author_str,AUTHOR_REGEX);
        line = re_smudge(line,filename,FILE_REGEX);
        line = re_smudge(line,date_str,DATE_REGEX);
        line = re_smudge(line,version_str,VER_REGEX);
        line = re_smudge(line,id_str,ID_REGEX);
        line = re_smudge(line,msg_str,MSG_REGEX);
        sys.stdout.write(line)

def clean(filename):
    for line in sys.stdin:
        line = re_clean(line,AUTHOR_REGEX);
        line = re_clean(line,FILE_REGEX)
        line = re_clean(line,DATE_REGEX)
        line = re_clean(line,VER_REGEX)
        line = re_clean(line,ID_REGEX)
        line = re_clean(line,MSG_REGEX)
        sys.stdout.write(line)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        _error("Error: missing commandline parameters %s or %s!" % (SMUDGE, CLEAN))
    if len(sys.argv) < 3:
        _error("Error: missing commandline parameters <filename>" )

    filename = sys.argv[2].strip()

    if sys.argv[1] == SMUDGE:
        smudge(filename)
    elif sys.argv[1] == CLEAN:
        clean(filename)
    else:
        _error("Error: first argument must be %s or %s" % (SMUDGE, CLEAN))
