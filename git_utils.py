#!/usr/bin/python3

import subprocess
import sys
import re

defaultBranches = ["master", "beta", "develop"]

# TODO: ammend, reverts?, interactive delete(con o sin pushear), pull requests(with jira comment), open pull request??

def printUsage():
        print("Usage: git_pull.py [OPTIONS] [BRANCHES]")
        print(f"Default branches to pull: {defaultBranches}")

def printAvailableArguments(args):
        print("List of available arguments:")
        for arg in args:
                print(f"\t* {arg}")

def sanitizeArguments(arguments):
        args = []
        parameters = []
        for item in arguments:
                if re.search(r"^-+", item):
                        args.append(item)
                else:
                        parameters.append(item)
        return (args, parameters)

def getCurrentBranch():
        return subprocess.run(r"git branch | grep \* | cut -d ' ' -f2",
                shell=True, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="UTF-8").stdout

def getBranchesToPull(args, branches=[], currentIdx=0):
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

def merge(params):
        target = params.pop(0)
        print(f"Merging {target} into {getCurrentBranch()}")
        subprocess.run(f"git merge {target}",shell=True)

def diff(params):
        target = params.pop(0)
        subprocess.run(f"git diff {target} {getCurrentBranch()}", shell=True)

def renameBranch(params):
        newName = params.pop(0)
        oldName = getCurrentBranch()
        print(f"New branch name: {oldName} => {newName}")
        subprocess.run(f"git branch -m {newName}", shell=True)
        subprocess.run(f"git push origin :{oldName}", shell=True)

def getCommitPrefix():
        branch = getCurrentBranch()
        prefix = re.search(r'^[A-Z]{3,4}-[0-9]{3,4}', branch)
        return (prefix.group() + ': ') if prefix is not None else ''

# TODO - Mejorar este checkeo
def checkNeedToPullAll(arguments):
        return ('-c' not in arguments) and ('-m' not in arguments)

def pullAll(arguments):
        currentBranch = getCurrentBranch()
        for branch in getBranchesToPull(arguments):
                print(f"--- Pulling from {branch}")
                pull(branch)
        subprocess.run(f"git checkout {currentBranch}", shell=True)

def commit(params):
        prefix = getCommitPrefix()
        subprocess.run("git add .", shell=True)
        subprocess.run(f"git commit -m '{prefix + params[0]}'", shell=True)

def main():
        arguments, parameters = sanitizeArguments(sys.argv[1:])
        
        if checkNeedToPullAll(arguments):
                pullAll(arguments)

        for arg in arguments:
                try:
                        args[arg](parameters)
                except KeyError:
                        printUsage()
                        printAvailableArguments(args)

args = {
        "--merge": merge,
        "--diff": diff,
        "-c": commit,
        "-m": renameBranch
}

if __name__ == "__main__":
        main()
