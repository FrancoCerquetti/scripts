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
        print(f"Merging {target} into {getCurrentBranch()}") # TODO - check si existe el branch a mergear
        subprocess.run(f"git merge {target}",shell=True)

def diff(args, argIdx):
        target = getValidArg(args, argIdx)
        subprocess.run(f"git diff {target} {getCurrentBranch()}", shell=True)

def main():
        currentBranch = getCurrentBranch()
        for branch in branches:
                print(f"--- Pulling from {branch}")
                pull(branch)
        subprocess.run(f"git checkout {currentBranch}", shell=True)
        
        arguments = sys.argv[1:]
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
        "--diff": diff
}

if __name__ == "__main__":
        main()
