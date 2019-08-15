#!/usr/bin/python3

import subprocess
import sys
import re

def printUsage():
        print("Usage: git_pull.py [OPTIONS] [BRANCH]")

def getCurrentBranch():
        return subprocess.run(r"git branch | grep \* | cut -d ' ' -f2",
                shell=True, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="UTF-8").stdout

def getValidArg(args, currentIdx):
        if re.search(r"^(--|-)", args[currentIdx]):
                return getValidArg(args, currentIdx + 1)
        else:
                return args[currentIdx]

def getBranchesToPull(args, branches=[], currentIdx=0):
        defaultBranches = ["master", "release", "develop"]
        
        if len(args) == 0:
                return defaultBranches

        if re.search(r"^(--|-)", args[currentIdx]):
                return branches if (len(branches) > 0) else defaultBranches
        else:
                branches.append(args[currentIdx])
                return getBranchesToPull(args, branches, currentIdx + 1)

def pull(branch):
        try:
                subprocess.run(f"git checkout {branch}",
                        shell=True, 
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                subprocess.run(f"git pull origin {branch}", shell=True)
        except subprocess.CalledProcessError:
                print(f"{branch} branch does not exist in this git repo, ignoring")

def merge(args, argIdx):
        target = getValidArg(args, argIdx)
        print(f"Merging {target} into {getCurrentBranch()}")
        subprocess.run(f"git merge {target}",shell=True)

def diff(args, argIdx):
        target = getValidArg(args, argIdx)
        subprocess.run(f"git diff {target} {getCurrentBranch()}", shell=True)

def getCommitPrefix():
        branch = getCurrentBranch()
        prefix = re.search(r'^[A-Z]{3}-[0-9]{3}', branch)
        return (prefix.group() + ': ') if prefix is not None else ''

def checkNeedToPullAll(arguments):
        for arg in arguments:
                if re.search(r'^-[a-z]*', arg):
                        return False
        return True

def pullAll(arguments):
        currentBranch = getCurrentBranch()
        for branch in getBranchesToPull(arguments):
                print(f"--- Pulling from {branch}")
                pull(branch)
        subprocess.run(f"git checkout {currentBranch}", shell=True)

def commit(args, argIdx):
        print("hola")
        prefix = getCommitPrefix()
        subprocess.run("git add .", shell=True)
        subprocess.run(f"git commit -m '{prefix + getValidArg(args, argIdx)}'", shell=True)


def main():
        arguments = sys.argv[1:]
        
        if checkNeedToPullAll(arguments):
                pullAll(arguments)

        for idx, arg in enumerate(arguments):
                try:
                        args[arg](arguments, idx)
                except KeyError:
                        pass
                except ValueError:
                        printUsage()

# Excluir branches
branches = ["master", "release", "develop"]
args = {
        "--merge": merge,
        "--diff": diff,
        "-c": commit
}

if __name__ == "__main__":
        main()
